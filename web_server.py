#!/usr/bin/env python3
"""
MGVRP Bot Web Management Server
Provides a web interface for managing the Discord bot
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import discord
from discord.ext import commands
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = Path("data")
WEB_DIR = Path("web")
GUILD_ID = int(os.getenv("GUILD_ID", "1277047315047120978"))

app = Flask(__name__, static_folder='web', template_folder='web')
CORS(app)

# Bot reference (will be set when bot starts)
bot_instance = None

class WebManager:
    def __init__(self, bot):
        self.bot = bot
        global bot_instance
        bot_instance = bot
    
    def get_bot_stats(self) -> Dict[str, Any]:
        """Get comprehensive bot statistics"""
        try:
            # Vehicle stats
            vehicles_file = DATA_DIR / "vehicles.json"
            total_vehicles = 0
            if vehicles_file.exists():
                with open(vehicles_file, 'r') as f:
                    vehicle_data = json.load(f)
                    total_vehicles = len(vehicle_data.get('vehicles', []))
            
            # Economy stats
            economy_file = DATA_DIR / "economy.json"
            total_users = 0
            if economy_file.exists():
                with open(economy_file, 'r') as f:
                    economy_data = json.load(f)
                    total_users = len(economy_data.get('users', {}))
            
            # Session stats
            sessions_file = DATA_DIR / "sessions.json"
            active_sessions = 0
            if sessions_file.exists():
                with open(sessions_file, 'r') as f:
                    session_data = json.load(f)
                    active_sessions = len([s for s in session_data.get('sessions', []) 
                                         if s.get('status') != 'Ended'])
            
            # Warning stats
            warnings_file = DATA_DIR / "warnings.json"
            total_warnings = 0
            if warnings_file.exists():
                with open(warnings_file, 'r') as f:
                    warning_data = json.load(f)
                    total_warnings = len(warning_data.get('data', []))
            
            # System stats
            import psutil
            memory_usage = f"{psutil.virtual_memory().percent}%"
            
            # Bot uptime
            if hasattr(self.bot, 'start_time'):
                uptime_delta = datetime.utcnow() - self.bot.start_time
                days = uptime_delta.days
                hours, remainder = divmod(uptime_delta.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                uptime = f"{days}d {hours}h {minutes}m"
            else:
                uptime = "Unknown"
            
            return {
                'totalVehicles': total_vehicles,
                'totalUsers': total_users,
                'activeSessions': active_sessions,
                'totalWarnings': total_warnings,
                'memoryUsage': memory_usage,
                'uptime': uptime,
                'botStatus': 'online' if self.bot.is_ready() else 'offline'
            }
        except Exception as e:
            logger.error(f"Error getting bot stats: {e}")
            return {
                'totalVehicles': 0,
                'totalUsers': 0,
                'activeSessions': 0,
                'totalWarnings': 0,
                'memoryUsage': 'N/A',
                'uptime': 'N/A',
                'botStatus': 'offline'
            }

# Initialize web manager
web_manager = None

# Routes
@app.route('/')
def index():
    """Serve the main web interface"""
    return send_from_directory('web', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('web', filename)

@app.route('/api/stats')
def get_stats():
    """Get bot statistics"""
    if web_manager:
        return jsonify(web_manager.get_bot_stats())
    return jsonify({'error': 'Bot not connected'}), 503

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    """Get all vehicles"""
    try:
        vehicles_file = DATA_DIR / "vehicles.json"
        if not vehicles_file.exists():
            return jsonify([])
        
        with open(vehicles_file, 'r') as f:
            data = json.load(f)
            vehicles = data.get('vehicles', [])
            
            # Add owner usernames if bot is available
            if bot_instance:
                guild = bot_instance.get_guild(GUILD_ID)
                if guild:
                    for vehicle in vehicles:
                        user_id = vehicle.get('userId')
                        if user_id:
                            member = guild.get_member(int(user_id))
                            vehicle['owner'] = member.display_name if member else f"User#{user_id}"
            
            return jsonify(vehicles)
    except Exception as e:
        logger.error(f"Error getting vehicles: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    """Add a new vehicle"""
    try:
        data = request.json
        vehicles_file = DATA_DIR / "vehicles.json"
        
        # Load existing data
        if vehicles_file.exists():
            with open(vehicles_file, 'r') as f:
                vehicle_data = json.load(f)
        else:
            vehicle_data = {'vehicles': []}
        
        # Create new vehicle
        new_vehicle = {
            'userId': data['owner'],
            'make': data['make'],
            'model': data['model'],
            'color': data['color'],
            'state': data['state'],
            'plate': data['plate'],
            'registeredAt': datetime.utcnow().isoformat()
        }
        
        vehicle_data['vehicles'].append(new_vehicle)
        
        # Save data
        with open(vehicles_file, 'w') as f:
            json.dump(vehicle_data, f, indent=2)
        
        return jsonify({'success': True, 'vehicle': new_vehicle})
    except Exception as e:
        logger.error(f"Error adding vehicle: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles/<vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    """Delete a vehicle"""
    try:
        vehicles_file = DATA_DIR / "vehicles.json"
        if not vehicles_file.exists():
            return jsonify({'error': 'Vehicle not found'}), 404
        
        with open(vehicles_file, 'r') as f:
            data = json.load(f)
        
        # Find and remove vehicle
        vehicles = data.get('vehicles', [])
        original_count = len(vehicles)
        
        # For simplicity, we'll remove by index (in a real implementation, use proper IDs)
        try:
            index = int(vehicle_id) - 1
            if 0 <= index < len(vehicles):
                vehicles.pop(index)
        except (ValueError, IndexError):
            return jsonify({'error': 'Invalid vehicle ID'}), 400
        
        if len(vehicles) == original_count:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # Save updated data
        with open(vehicles_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting vehicle: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/economy', methods=['GET'])
def get_economy():
    """Get economy data"""
    try:
        economy_file = DATA_DIR / "economy.json"
        if not economy_file.exists():
            return jsonify({'users': []})
        
        with open(economy_file, 'r') as f:
            data = json.load(f)
            users = []
            
            # Convert user data to list format
            for user_id, user_data in data.get('users', {}).items():
                if bot_instance:
                    guild = bot_instance.get_guild(GUILD_ID)
                    if guild:
                        member = guild.get_member(int(user_id))
                        username = member.display_name if member else f"User#{user_id}"
                    else:
                        username = f"User#{user_id}"
                else:
                    username = f"User#{user_id}"
                
                users.append({
                    'id': user_id,
                    'username': username,
                    'balance': user_data.get('balance', 0),
                    'bank': user_data.get('bank', 0),
                    'lastActive': user_data.get('last_daily') or user_data.get('last_work') or datetime.utcnow().isoformat()
                })
            
            return jsonify({'users': users})
    except Exception as e:
        logger.error(f"Error getting economy data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/economy/action', methods=['POST'])
def economy_action():
    """Perform economy action"""
    try:
        data = request.json
        user_id = data['user']
        action = data['action']
        amount = data['amount']
        target = data['target']
        
        economy_file = DATA_DIR / "economy.json"
        
        # Load existing data
        if economy_file.exists():
            with open(economy_file, 'r') as f:
                economy_data = json.load(f)
        else:
            economy_data = {'users': {}}
        
        # Initialize user if not exists
        if user_id not in economy_data['users']:
            economy_data['users'][user_id] = {
                'balance': 0,
                'bank': 0,
                'total_earned': 0,
                'total_spent': 0
            }
        
        user_data = economy_data['users'][user_id]
        
        # Perform action
        if action == 'add':
            user_data[target] += amount
            user_data['total_earned'] += amount
        elif action == 'remove':
            user_data[target] = max(0, user_data[target] - amount)
            user_data['total_spent'] += amount
        elif action == 'set':
            user_data[target] = amount
        
        # Save data
        with open(economy_file, 'w') as f:
            json.dump(economy_data, f, indent=2)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error performing economy action: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions"""
    try:
        sessions_file = DATA_DIR / "sessions.json"
        if not sessions_file.exists():
            return jsonify([])
        
        with open(sessions_file, 'r') as f:
            data = json.load(f)
            sessions = data.get('sessions', [])
            
            # Add host usernames if bot is available
            if bot_instance:
                guild = bot_instance.get_guild(GUILD_ID)
                if guild:
                    for session in sessions:
                        host_id = session.get('host_id')
                        if host_id:
                            member = guild.get_member(int(host_id))
                            session['host'] = member.display_name if member else f"User#{host_id}"
            
            return jsonify(sessions)
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create a new session"""
    try:
        data = request.json
        sessions_file = DATA_DIR / "sessions.json"
        
        # Load existing data
        if sessions_file.exists():
            with open(sessions_file, 'r') as f:
                session_data = json.load(f)
        else:
            session_data = {'sessions': []}
        
        # Create new session
        new_session = {
            'id': len(session_data['sessions']) + 1,
            'host_id': data['host'],
            'cohost_id': data.get('cohost'),
            'priority': data['priority'],
            'frp_speed': data['frpSpeed'],
            'house_claiming': 'Yes' if data['houseClaming'] else 'No',
            'session_link': data['link'],
            'status': 'Setting Up',
            'participants': [],
            'created_at': datetime.utcnow().isoformat()
        }
        
        session_data['sessions'].append(new_session)
        
        # Save data
        with open(sessions_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return jsonify({'success': True, 'session': new_session})
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<session_id>/end', methods=['POST'])
def end_session(session_id):
    """End a session"""
    try:
        sessions_file = DATA_DIR / "sessions.json"
        if not sessions_file.exists():
            return jsonify({'error': 'Session not found'}), 404
        
        with open(sessions_file, 'r') as f:
            data = json.load(f)
        
        # Find and update session
        sessions = data.get('sessions', [])
        for session in sessions:
            if str(session['id']) == session_id:
                session['status'] = 'Ended'
                session['ended_at'] = datetime.utcnow().isoformat()
                break
        else:
            return jsonify({'error': 'Session not found'}), 404
        
        # Save updated data
        with open(sessions_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/moderation', methods=['GET'])
def get_moderation():
    """Get moderation data"""
    try:
        warnings_file = DATA_DIR / "warnings.json"
        actions = []
        total_warnings = 0
        
        if warnings_file.exists():
            with open(warnings_file, 'r') as f:
                warning_data = json.load(f)
                warnings = warning_data.get('data', [])
                total_warnings = len(warnings)
                
                # Convert warnings to actions format
                if bot_instance:
                    guild = bot_instance.get_guild(GUILD_ID)
                    for warning in warnings[-20:]:  # Last 20 warnings
                        user_id = warning.get('user_id')
                        mod_id = warning.get('moderator_id')
                        
                        user_name = f"User#{user_id}"
                        mod_name = f"Mod#{mod_id}"
                        
                        if guild:
                            user = guild.get_member(int(user_id))
                            moderator = guild.get_member(int(mod_id))
                            if user:
                                user_name = user.display_name
                            if moderator:
                                mod_name = moderator.display_name
                        
                        actions.append({
                            'user': user_name,
                            'action': 'Warning',
                            'reason': warning.get('reason', 'No reason'),
                            'moderator': mod_name,
                            'date': warning.get('timestamp'),
                            'status': 'Active'
                        })
        
        return jsonify({
            'totalWarnings': total_warnings,
            'activeTimeouts': 0,  # Would need to track timeouts separately
            'recentBans': 0,      # Would need to track bans separately
            'actions': actions
        })
    except Exception as e:
        logger.error(f"Error getting moderation data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/moderation/action', methods=['POST'])
def moderation_action():
    """Perform moderation action"""
    try:
        data = request.json
        # This would integrate with the bot's moderation system
        # For now, just return success
        return jsonify({'success': True, 'message': 'Moderation action would be performed via bot'})
    except Exception as e:
        logger.error(f"Error performing moderation action: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get guild users"""
    try:
        if not bot_instance:
            return jsonify({'error': 'Bot not connected'}), 503
        
        guild = bot_instance.get_guild(GUILD_ID)
        if not guild:
            return jsonify({'error': 'Guild not found'}), 404
        
        users = []
        for member in guild.members[:50]:  # Limit to first 50 members
            users.append({
                'id': str(member.id),
                'username': member.display_name,
                'avatar': str(member.avatar.url) if member.avatar else str(member.default_avatar.url),
                'joinedAt': member.joined_at.isoformat() if member.joined_at else None,
                'roles': [role.name for role in member.roles if role.name != '@everyone'],
                'status': str(member.status).title()
            })
        
        return jsonify(users)
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Get or update bot settings"""
    settings_file = DATA_DIR / "settings.json"
    
    if request.method == 'GET':
        try:
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    return jsonify(json.load(f))
            else:
                # Default settings
                default_settings = {
                    'botPrefix': '!',
                    'currencySymbol': '$',
                    'dailyReward': 1000,
                    'weeklyReward': 5000,
                    'autobanThreshold': 5,
                    'defaultTimeout': 60
                }
                return jsonify(default_settings)
        except Exception as e:
            logger.error(f"Error getting settings: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            settings_data = request.json
            
            # Save settings
            with open(settings_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
            
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return jsonify({'error': str(e)}), 500

def start_web_server(bot, host='0.0.0.0', port=5000):
    """Start the web server"""
    global web_manager
    web_manager = WebManager(bot)
    
    logger.info(f"Starting web server on {host}:{port}")
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    # For testing without bot
    app.run(host='0.0.0.0', port=5000, debug=True)