"""
CRM API Routes for Lead Management
Import these routes into app.py to add CRM endpoints
"""
from flask import jsonify, request, g
from crm_db import (
    get_leads_with_filters, save_lead, update_lead_status, 
    get_leads_stats
)

def get_db():
    """Get database connection from Flask g object"""
    return g._database

# API Routes for CRM

def api_get_leads():
    """GET /api/leads - Get all leads with optional filtering"""
    try:
        status = request.args.get('status', 'all')
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'DESC')
        
        db = get_db()
        leads = get_leads_with_filters(db, status, sort_by, order)
        return jsonify({'success': True, 'leads': leads})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def api_save_lead():
    """POST /api/leads - Save or update a lead"""
    try:
        data = request.get_json()
        if not data.get('url'):
            return jsonify({'success': False, 'error': 'URL is required'}), 400
        
        db = get_db()
        save_lead(db, data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def api_update_lead_status(lead_id):
    """PATCH /api/leads/<id>/status - Quick status update"""
    try:
        data = request.get_json()
        status = data.get('status')
        if not status:
            return jsonify({'success': False, 'error': 'Status is required'}), 400
        
        db = get_db()
        update_lead_status(db, lead_id, status)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def api_update_follow_up(lead_id):
    """PATCH /api/leads/<id>/follow-up - Set follow-up date"""
    try:
        data = request.get_json()
        follow_up_date = data.get('followUpDate')
        
        db = get_db()
        db.execute('''
            UPDATE leads SET follow_up_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (follow_up_date, lead_id))
        db.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def api_delete_lead(lead_id):
    """DELETE /api/leads/<id> - Delete a lead"""
    try:
        db = get_db()
        db.execute('DELETE FROM leads WHERE id = ?', (lead_id,))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def api_get_stats():
    """GET /api/leads/stats - Get dashboard statistics"""
    try:
        db = get_db()
        stats = get_leads_stats(db)
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Function to register all CRM routes with Flask app
def register_crm_routes(app):
    """Register all CRM routes with the Flask app"""
    
    # Leads endpoints
    app.add_url_rule('/api/leads', 'get_leads', api_get_leads, methods=['GET'])
    app.add_url_rule('/api/leads', 'save_lead', api_save_lead, methods=['POST'])
    app.add_url_rule('/api/leads/<int:lead_id>/status', 'update_lead_status', api_update_lead_status, methods=['PATCH'])
    app.add_url_rule('/api/leads/<int:lead_id>/follow-up', 'update_follow_up', api_update_follow_up, methods=['PATCH'])
    app.add_url_rule('/api/leads/<int:lead_id>', 'delete_lead', api_delete_lead, methods=['DELETE'])
    app.add_url_rule('/api/leads/stats', 'get_stats', api_get_stats, methods=['GET'])
    
    print("✓ CRM routes registered")
