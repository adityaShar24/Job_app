from flask import Blueprint , request , make_response 
import json
import bson.json_util as json_util
from database import jobs_collections , applicants_collections , users_collections
from email_validator import validate_email, EmailNotValidError
from bson.objectid import ObjectId


job_bp = Blueprint("job_bp" , __name__)

@job_bp.post("/job_posts")
def Posts():
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
    

@job_bp.post("/apply")
def Apply():
    body = json.loads(request.data) 
    applicant = {
        'job_id':body['job_id'],
        'username':body['username'] ,
        'email': body['email'],
        'resume':body['resume'],
        'contact_no':body['contact_no'],
        'cover_letter':body['cover_letter']
        
    }
    
    for field in ['username','email','resume','contact_no','cover_letter']:
        if not applicant.get(field):
            return make_response({'message': f"{field} cannot be empty."} , 400)
        
    jobs = jobs_collections.find_one({"_id": ObjectId(applicant["job_id"])})
    users = users_collections.find_one({'username':body['username']})
    
    if len(applicant['contact_no']) != 10:
        return make_response({'message': 'Contact number should be of 10 digits.'}, 400)
    
    if not jobs:
        return make_response({"message": "Job not found."}, 404)
    
    if not users: 
        return make_response({'message':'User not found'} , 404)
    
    saved_applicants = applicants_collections.insert_one(applicant).inserted_id
    jsonVersion = json_util.dumps(saved_applicants)
    
    return make_response({"message": "Application submitted successfully." , 'applicant':jsonVersion}, 200)
