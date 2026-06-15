import datetime
import os
import pytz
from jinja2 import Environment, FileSystemLoader
from google.cloud import firestore
import functions_framework

# Initialize Firestore client
db = firestore.Client()

# Configure Jinja2 to load templates using the absolute path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

@functions_framework.http
def render_dashboard(request):
    """
    Cloud Function that retrieves data from Firestore and renders an HTML dashboard.
    """
    try:
        madrid_tz = pytz.timezone('Europe/Madrid')
        now = datetime.datetime.now(madrid_tz)
        
        # 1. Get the most recent occupancy (approx last scraped hour)
        # Since scraper.py saves timestamp, we look for the most recent documents.
        # An efficient way without complex indexing is to search the last hour if we know
        # it runs every 15 mins.
        one_hour_ago = now - datetime.timedelta(hours=1)
        
        latest_readings_ref = db.collection('pool_readings').where(
            "timestamp", ">=", one_hour_ago
        ).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(100).stream()
        
        # Group by pool and keep the most recent reading for each
        latest_by_pool = {}
        for doc in latest_readings_ref:
            data = doc.to_dict()
            name = data.get('name')
            if not name:
                continue
                
            # Filter to keep only the requested indoor pools
            name_upper = name.upper()
            is_alberto_maestro = "CDM ALBERTO MAESTRO" in name_upper and "VERANO" not in name_upper
            is_jose_garces = "CDM JOSE GARCES" in name_upper
            is_palafox = "CDM PALAFOX" in name_upper
            is_siglo_xxi = "CDM SIGLO XXI" in name_upper
            
            if not (is_alberto_maestro or is_jose_garces or is_palafox or is_siglo_xxi):
                continue
                
            # Save only if we haven't seen it, as they are sorted DESC, the first is the most recent
            if name not in latest_by_pool:
                capacity = data.get('capacity', 0)
                current = data.get('current_occupation', 0)
                
                # Handle Nones
                capacity = capacity if capacity is not None else 0
                current = current if current is not None else 0
                
                percentage = int((current / capacity) * 100) if capacity > 0 else 0
                
                latest_by_pool[name] = {
                    'name': name,
                    'current': current,
                    'capacity': data.get('capacity', 'N/A'),
                    'percentage': percentage,
                    'is_open': capacity > 0 and data.get('capacity') is not None,
                    'timestamp': data.get('timestamp')
                }
        
        # Sort alphabetically
        current_status = sorted(list(latest_by_pool.values()), key=lambda x: x['name'])


        # 2. Get statistics for the last 4 weeks (28 days)
        # Limited to not exceed free Firestore reads, adequate for an MVP.
        four_weeks_ago = now - datetime.timedelta(days=28)
        
        historical_ref = db.collection('pool_readings').where(
            "timestamp", ">=", four_weeks_ago
        ).stream()

        # In-memory aggregation (grouping by pool, day of week and hour)
        stats = {}
        # Structure of stats:
        # {
        #   "POOL A": {
        #       "Monday": { 7: [10, 15, ...], 8: [...], ... },
        #       "Tuesday": ...
        #   }
        # }
        
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for doc in historical_ref:
            data = doc.to_dict()
            name = data.get('name')
            ts = data.get('timestamp')
            current = data.get('current_occupation')
            
            if not name or current is None or not ts:
                continue
                
            # Filter to keep only the requested indoor pools
            name_upper = name.upper()
            is_alberto_maestro = "CDM ALBERTO MAESTRO" in name_upper and "VERANO" not in name_upper
            is_jose_garces = "CDM JOSE GARCES" in name_upper
            is_palafox = "CDM PALAFOX" in name_upper
            is_siglo_xxi = "CDM SIGLO XXI" in name_upper
            
            if not (is_alberto_maestro or is_jose_garces or is_palafox or is_siglo_xxi):
                continue
                
            # Convert timestamp to Madrid time if it's naive or from another zone
            if ts.tzinfo is None:
                ts = madrid_tz.localize(ts)
            else:
                ts = ts.astimezone(madrid_tz)
                
            day = days_of_week[ts.weekday()] # 0 is Monday
            hour = ts.hour
            
            # Consider opening hours only (approx 7 to 22)
            if hour < 7 or hour > 22:
                continue

            if name not in stats:
                stats[name] = {d: {h: [] for h in range(7, 23)} for d in days_of_week}
                
            stats[name][day][hour].append(current)

        # Calculate averages
        # Final structure for the frontend:
        # { "POOL A": { "Monday": [avg_7, avg_8, ... avg_22], "Tuesday": [...] } }
        
        weekly_stats = {}
        for pool_name, days_data in stats.items():
            weekly_stats[pool_name] = {}
            for day, hours_data in days_data.items():
                averages = []
                for h in range(7, 23):
                    readings = hours_data[h]
                    avg = int(sum(readings) / len(readings)) if readings else 0
                    averages.append(avg)
                weekly_stats[pool_name][day] = averages

        # 3. Enhance current_status with trend info relative to right now
        current_day_name = days_of_week[now.weekday()]
        current_hour = now.hour

        for pool in current_status:
            pool_name = pool['name']
            
            # Default empty trend data
            pool['trend_percent'] = 0
            pool['trend_absolute'] = 0
            pool['has_trend'] = False
            pool['historical_avg'] = 0

            if pool['is_open'] and current_hour >= 7 and current_hour <= 22:
                # Find the average for the current hour
                try:
                    hour_index = current_hour - 7
                    historical_avg = weekly_stats[pool_name][current_day_name][hour_index]
                    
                    pool['historical_avg'] = historical_avg
                    
                    if historical_avg > 0:
                        diff = pool['current'] - historical_avg
                        # +50% means there are 50% more people than the average.
                        trend_percent = int((diff / historical_avg) * 100)
                        
                        pool['trend_absolute'] = diff
                        pool['trend_percent'] = trend_percent
                        pool['has_trend'] = True
                        
                except (KeyError, IndexError):
                    pass


        # 4. Render template
        template = env.get_template('index.html')
        current_day_name = days_of_week[now.weekday()]
        html_content = template.render(
            current_status=current_status,
            weekly_stats=weekly_stats,
            current_day_name=current_day_name,
            current_hour=current_hour,
            last_updated=now.strftime("%Y-%m-%d %H:%M")
        )
        
        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}

    except Exception as e:
        print(f"Error generating dashboard: {e}")
        return f"<h1>Internal Server Error</h1><p>{str(e)}</p>", 500
