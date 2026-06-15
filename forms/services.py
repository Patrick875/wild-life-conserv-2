import requests
import os
from dotenv import load_dotenv
from forms.helpers import *
from warning.models import Warning
from warning_feedbacks.models import WarningFeedback
from extensions import db
from sqlalchemy import and_

load_dotenv()

kobo_timeout = int(os.getenv("KOBO_TIMEOUT", 15))
kobo_token = os.getenv("KOBO_API_TOKEN")
KOBO_BASE_URL= os.getenv("KOBO_SERVER_URL")

headers = {
        "Authorization": f"Token {kobo_token}",
        "Content-Type": "application/json"
}

def get_forms():
    try:
       
        KOBO_TOKEN=os.getenv("KOBO_API_TOKEN")
        url = f"{KOBO_BASE_URL}/api/v2/assets/?asset_type=survey"

        headers = {
                "Authorization": f"Token {KOBO_TOKEN}",
                "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers, timeout=15)
       
        if not response.ok:
            raise ValueError(response.text)
        print(response.json())
        return response.json()
        
    except ValueError as error:
        raise ValueError("Error fetching forms")


def get_form_by_uuid(uuid:str):
    
    try:
        KOBO_BASE_URL= os.getenv("KOBO_SERVER_URL")
        # response=make_kobo_request(method='GET',url=KOBO_BASE_URL+"/api/v2/assets/"+uuid)
        response=requests.get(KOBO_BASE_URL+"/api/v2/assets/"+uuid,headers=headers,timeout=kobo_timeout)
        print("form response",response)
        return response.json()
        
    except ValueError as error:
        raise(f"Error fetching form {str(error)}")
     

def get_parsed_form( form_uid: str) :
        """Get form and parse it for mobile app consumption"""
        try:
            form_data = get_form_by_uuid(form_uid)
            if not form_data:
                return None
            
            parsed_form = parse_form_content(form_data)
            return parsed_form
        except Exception as e:
            raise ValueError(f"Failed to parse form {form_uid}: {e}")
            


def get_form_submissions(
        form_uid: str, 
        limit: int = 100, 
        start: int = 0,
        sort: str = "-_submission_time"
    ) :
        """Get submissions for a specific form"""
        try:
            params = {
                # "limit": limit,
                # "start": start,
                # "sort": sort,
                "format": "json"
            }
            
            response=requests.get(KOBO_BASE_URL+"/api/v2/assets/"+form_uid+"/data",headers=headers,timeout=kobo_timeout)
            submissions = Warning.query.order_by(Warning.created_at.desc()).filter_by(kobo_form_id=form_uid).all()
            
            submissions_normalized=[submission.to_dict(include_feedbacks=True) for submission in submissions] or []
           
            return {
                "api_results":submissions_normalized,
                "count": len(submissions_normalized),
                "next": response.json().get("next"),
                "previous": response.json().get("previous")
            }
            
        except Exception as e:
            raise ValueError(f"Failed to get submissions for form {form_uid}: {e}")

def get_submissions_by_user(form_id:int,user_id:int):
     submissions = Warning.query.order_by(Warning.created_at.desc()).filter(and_(Warning.user_id==user_id,Warning.kobo_form_id==form_id)).all()
     submissions_normalized=[submission.to_dict(include_feedbacks=True) for submission in submissions] or []
     return {
            "api_results":submissions_normalized,
            "count": len(submissions_normalized),
            }

def submit_warning(form_uuid: str, submission_data: dict,user_id:int):
    """
    xml_form_id : the form's id_string  (e.g. "aXxYyZz123")
                  GET https://kc.kobotoolbox.org/api/v1/forms?format=json
                  and find  "id_string"  for your form.

    form_uuid   : the form-level UUID   (e.g. "f739945244514a6bb304dc35d6049880")
                  same endpoint, field  "uuid".
                  This is NOT the submission UUID — it identifies the form schema.
    """
    submission = build_submission_dict(submission_data)

    # Inject formhub/uuid — required by KoboCAT to route the submission
    submission["formhub"] = {"uuid": form_uuid}

    payload = {
        "id": form_uuid,
        "submission": submission,
    }

    warning=Warning(
        kobo_form_id = form_uuid,
        submission_data = submission,
        user_id = user_id
      )
    
    db.session.add(warning)
    db.session.flush()

    submit_headers = {
        "Authorization": headers.get("Authorization"),
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{KOBO_BASE_URL}/api/v1/submissions",  # must be kc. subdomain, not kf.
        headers=submit_headers,
        json=payload,
        timeout=30,
    )

    print(f'\n\n\n\n this is submission-response {response.json()} \n\n\n\n\n\n ')
    
    if not response.ok:
        raise ValueError(
            f"Kobo submit failed: {response.status_code} {response.text}"
        )
    
    kobo_response=response.json()
    submission_id=kobo_response.get("instanceID").replace("uuid:","")
    warning.status='submitted'
    warning.kobo_submission_id=submission_id
    
    db.session.commit()

    return response.json() if response.text else {"success": True}

def update_submission(
      
        form_uid: str, 
        submission_id: str, 
        submission_data: dict
    ) :
        """Update an existing submission"""
        try:
            # response = make_kobo_request(
            #     "PUT",
            #     f"/api/v2/assets/{form_uid}/submissions/{submission_id}/",
            #     data=submission_data
            # )
            warning = Warning.query.filter_by(id=submission_id, kobo_form_id=form_uid).first()
            kobo_submission_id = warning.kobo_submission_id if warning else submission_id
            response=requests.put(KOBO_BASE_URL+"/api/v2/assets/"+form_uid+"/submissions/"+kobo_submission_id,headers=headers,timeout=kobo_timeout,json=submission_data)
            if not response.ok:
                raise ValueError(response.text)

            if warning:
                warning.submission_data = submission_data
                db.session.commit()

            # logger.info(f"Successfully updated submission {submission_id}")
            return response.json() if response.text else {"success": response.ok}
            
        except Exception as e:
            raise ValueError(f"Failed to update submission {submission_id}: {e}")
    
def delete_submission(
   
        form_uid: str, 
        submission_id: str
    ) -> bool:
        """Delete a submission"""
        try:
            # make_kobo_request(
            #     "DELETE",
            #     f"/api/v2/assets/{form_uid}/submissions/{submission_id}/"
            # )
            warning = Warning.query.filter_by(id=submission_id, kobo_form_id=form_uid).first()
            kobo_submission_id = warning.kobo_submission_id if warning else submission_id
            response = requests.delete(KOBO_BASE_URL+"/api/v2/assets/"+form_uid+"/submissions/"+kobo_submission_id,headers=headers,timeout=kobo_timeout)
            if not response.ok:
                raise ValueError(response.text)

            if warning:
                WarningFeedback.query.filter_by(warning_id=warning.id).delete()
                db.session.delete(warning)
                db.session.commit()
            
            # logger.info(f"Successfully deleted submission {submission_id}")
            return {"success": response.ok}
            
        except Exception as e:
            raise ValueError(f"Failed to delete submission {submission_id}: {e}")
            
    
def get_form_schema( form_uid: str):
        """Get the JSON schema for a form"""
        try:
            form_data = get_form_by_uuid(form_uid)
            if not form_data:
                return None
            
            content = form_data.get("content", {})
            return {
                "survey": content.get("survey", []),
                "choices": content.get("choices", []),
                "settings": content.get("settings", {})
            }
            
        except Exception as e:
            # logger.error(f"Failed to get form schema {form_uid}: {e}")
            raise ValueError(f"Failed to get form schema {form_uid}: {e}")
    
