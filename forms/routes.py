from flask import Blueprint,request
from forms.services import *
from utils.api_response import api_response
forms_bp=Blueprint("forms_bp",__name__)

@forms_bp.route('/',methods=['GET'])
def get_kobo_forms():
    try:
        forms= get_forms()
        print (forms)
        return api_response(
            success=True,
            message="Forms fetched successfully",
            data=forms,
            status_code=200
        )

    except ValueError as error:
        return api_response(
            success=False,
            message='Error fetching forms',
            errors=str(error),
            status_code=500
        )

@forms_bp.route('/<uuid>',methods=['GET'])
def get_form_details(uuid:str):
    
    try:
       
        response=get_form_by_uuid(uuid)
        print("form response",response)
        return api_response(
            success=True,
            message="Form fetched successfully",
            data=response,
            status_code=200
        )
    except ValueError as error:
        return api_response(
            success=False,
            message='Error fetching form details',
            errors=str(error),
            status_code=500
        )

@forms_bp.route('/<form_uuid>/submissions',methods=['GET'])
def get_submissions_per_form(form_uuid) :
        try:
            response = get_form_submissions(form_uuid)

            return api_response(
            success=True,
            data=response,
            message='Form submissions fetched successfuly',
         
            )
                        
            
        except Exception as e:
            return api_response(
            success=False,
            message='Error fetching submissions',
            errors=str(e),
            status_code=500
            )

@forms_bp.route('/<form_uuid>/submit_warning',methods=['POST'])   
def submit_data( 
        form_uuid: str ) :
        submission_data=request.json
        print(submission_data)
        try:
             
            response = submit_warning(form_uuid=form_uuid,submission_data=submission_data)
            
            # logger.info(f"Successfully submitted data to form {form_uid}")
            return api_response(
            success=True,
            message='Warning submitted successfuly',
            data=response,
            status_code=200
        )
            
        except Exception as e:
            return api_response(
            success=False,
            message='Error submitting warning',
            errors=str(e),
            status_code=400
            )
            
@forms_bp.route('/<form_uuid>/submissions/<warn_id>',methods=['PUT'])     
def update_form_submission(
      
        form_uuid: str, 
        warn_id: str, 
        submission_data: dict
    ) :
        
        try:
            response = update_submission(form_uid=form_uuid,submission_id=submission_data,id=warn_id)
            
            # logger.info(f"Successfully updated submission {submission_id}")
            return api_response(
            success=True,
            message='Warning updated successfuly',
            data=response,
            status_code=203
            )
            
        except Exception as e:
            return api_response(
            success=False,
            message='Error updating submission',
            errors=str(e),
            status_code=400
            )

@forms_bp.route('/<form_uuid>/submissions/<warn_id>',methods=['DELETE'])   
def delete_warn(form_uuid: str, warn_id: str) :
        try:
            
            response=delete_submission(form_uuid=form_uuid,submission_id=warn_id)
            
            # logger.info(f"Successfully deleted submission {submission_id}")
            return api_response(
            success=True,
            message='Warning deleted successfuly',
            data=response,
            status_code=203
            )
            
        except Exception as e:
             return api_response(
            success=False,
            message='Error deleting submission',
            errors=str(e),
            status_code=400
            )
  