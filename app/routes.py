# app/routes.py
from flask import Blueprint, jsonify, request
from app.models import InvestmentOpportunity
from app.utils import require_api_key
import secrets 

api = Blueprint('api', __name__)

@api.route('/opportunities')
@require_api_key
def get_opportunities():
    """
    Get list of investment opportunities
    ---
    tags:
      - Opportunities
    parameters:
      - name: country
        in: query
        type: string
        required: false
        default: Kenya
        description: Filter by country
      - name: type
        in: query
        type: string
        required: false
        enum: [bond, ipo, share_offer]
        description: Filter by opportunity type
      - name: X-API-Key
        in: header
        type: string
        required: true
        description: Your API key
    responses:
      200:
        description: A list of opportunities
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              source:
                type: string
              url:
                type: string
              country:
                type: string
              type:
                type: string
              published_date:
                type: string
                format: date-time
      401:
        description: Missing or invalid API key
      429:
        description: Monthly quota exceeded
    """
    country = request.args.get('country', 'Kenya')
    opp_type = request.args.get('type')
    
    query = InvestmentOpportunity.query.filter_by(country=country)
    if opp_type:
        query = query.filter_by(type=opp_type)
    
    results = query.order_by(InvestmentOpportunity.published_date.desc()).limit(50).all()
    
    return jsonify([{
        'id': o.id,
        'title': o.title,
        'source': o.source,
        'url': o.url,
        'country': o.country,
        'type': o.type,
        'published_date': o.published_date.isoformat()
    } for o in results])

# import secrets

@api.route('/admin/generate-key', methods=['POST'])
def generate_key():
    """
    Generate an API key (admin only)
    ---
    tags:
      - Admin
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: user@example.com
            secret:
              type: string
              example: YOUR_ADMIN_PASSWORD
    responses:
      200:
        description: API key created
        schema:
          type: object
          properties:
            api_key:
              type: string
      403:
        description: Unauthorized
    """
    if request.json.get('secret') != 'YOUR_ADMIN_PASSWORD':
        return jsonify({"error": "Unauthorized"}), 403
    email = request.json['email']
    key = secrets.token_urlsafe(32)
    from app.models import APIKey, db
    new_key = APIKey(key=key, email=email, request_limit=1000)
    db.session.add(new_key)
    db.session.commit()
    return jsonify({"api_key": key})