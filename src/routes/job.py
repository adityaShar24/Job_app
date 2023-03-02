from flask import Blueprint , request , make_response 
import json
import bson.json_util as json_util
from database import jobs_collections
from email_validator import validate_email, EmailNotValidError


job_bp = Blueprint("job_bp" , __name__)

@job_bp.post("/job_posts")
def Apply():
    body = json.loads(request.data)
    Jobs = {
        "title":body["title"],
        "company":body["company"],
        "location":body["location"],
        "description":body["description"],
        "requirements":body["requirements"],
        "contact_email":body["contact_email"] , 
        "workfromhome": False
    }
    
    for field in ['title', 'company', 'location', 'description', 'requirements', 'contact_email']:
        if not Jobs.get(field):
            return make_response({"message": f"{field} cannot be empty."}, 400)
    
    if "workfromhome" not in body:
        if "remote" in body["location"].lower() or "work from home" in body["description"].lower():
            Jobs["workfromhome"] = True
            
    try:
        valid_email = validate_email(body["contact_email"])
        saved_jobs = jobs_collections.insert_one(Jobs).inserted_id
        jsonVersion = json_util.dumps(saved_jobs)
        return make_response({'message':'Job posted succesfully' , 'job': jsonVersion} , 200)
    
    except EmailNotValidError as e:
        return make_response({"error": "Invalid email address"}, 400)
    
    