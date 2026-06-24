from flask import Blueprint,request
from forms.services import *
from utils.api_response import api_response
from flask_jwt_extended import jwt_required,get_jwt_identity
forms_bp=Blueprint("forms_bp",__name__)

@forms_bp.route('/',methods=['GET'])
def get_kobo_forms():
    """List available KoboToolbox survey forms.
    ---
    tags:
      - Kobo forms
    responses:
      200:
        description: Kobo survey forms fetched successfully.
      500:
        description: KoboToolbox could not be reached or returned an error.
    """
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
    """Get a Kobo form definition for client-side rendering.
    ---
    tags:
      - Kobo forms
    parameters:
      - name: uuid
        in: path
        type: string
        required: true
        description: KoboToolbox asset UID for the survey form.
    responses:
      200:
        description: Form metadata and question definition fetched successfully.
      500:
        description: KoboToolbox could not be reached or returned an error.
    """
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
@jwt_required(locations=['headers',])
def get_submissions_per_form(form_uuid) :
        """List submissions for a Kobo form.
        ---
        tags:
          - Kobo submissions
        security:
          - BearerAuth: []
        parameters:
          - name: form_uuid
            in: path
            type: string
            required: true
            description: KoboToolbox asset UID for the survey form.
        responses:
          200:
            description: Form submissions fetched successfully.
          401:
            description: A valid bearer token was not supplied.
          500:
            description: KoboToolbox could not be reached or returned an error.
        """
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

@forms_bp.route('/<form_uuid>/submissions/me',methods=['GET'])
@jwt_required(locations=['headers',])
def get_my_submissions(form_uuid):
    """List the authenticated user's local submissions for a Kobo form.
    ---
    tags:
      - Kobo submissions
    security:
      - BearerAuth: []
    parameters:
      - name: form_uuid
        in: path
        type: string
        required: true
        description: KoboToolbox asset UID for the survey form.
    responses:
      200:
        description: The caller's submissions fetched successfully.
      401:
        description: A valid bearer token was not supplied.
      500:
        description: Submissions could not be fetched.
    """
    try:    
            user_id=int(get_jwt_identity())
            response =  get_submissions_by_user(form_id=form_uuid,user_id=user_id)

            return api_response(
            success=True,
            data=response,
            message='Form submissions by user fetched successfuly',
         
            )
                        
            
    except Exception as e:
            print(e)
            return api_response(
            success=False,
            message='Error fetching submissions',
            errors=str(e),
            status_code=500
            )

@forms_bp.route('/<form_uuid>/submit_warning',methods=['POST'])   
@jwt_required(locations=['headers','cookies'])
def submit_data( 
        form_uuid: str ) :
        """Submit a warning to KoboToolbox and persist its local linkage.
        ---
        tags:
          - Kobo submissions
        security:
          - BearerAuth: []
        consumes:
          - application/json
        parameters:
          - name: form_uuid
            in: path
            type: string
            required: true
            description: KoboToolbox asset UID for the survey form.
          - name: body
            in: body
            required: true
            description: Submission fields must match the question names and types in the Kobo form definition.
            schema:
              type: object
              additionalProperties: true
        responses:
          200:
            description: Warning submitted successfully. The response includes local and Kobo submission identifiers.
          400:
            description: The payload is invalid or KoboToolbox rejected the submission.
          401:
            description: A valid bearer token was not supplied.
        """
        submission_data=request.json
        try:
            user_id=int(get_jwt_identity())
            response = submit_warning(form_uuid=form_uuid,submission_data=submission_data,user_id=user_id)
            
            # logger.info(f"Successfully submitted data to form {form_uid}")
            return api_response(
            success=True,
            message='Warning submitted successfuly',
            data=response,
            status_code=200
        )
            
        except Exception as e:
            print(str(e))
            return api_response(
            success=False,
            message='Error submitting warning',
            errors=str(e),
            status_code=400
            )

@forms_bp.route('/<form_uuid>/submissions/<warn_id>',methods=['PUT'])     
@jwt_required(locations=['headers'])        
def update_form_submission(
        form_uuid: str, 
        warn_id: str
    ) :
        """Update an existing Kobo-backed warning submission.
        ---
        tags:
          - Kobo submissions
        security:
          - BearerAuth: []
        consumes:
          - application/json
        parameters:
          - name: form_uuid
            in: path
            type: string
            required: true
            description: KoboToolbox asset UID for the survey form.
          - name: warn_id
            in: path
            type: string
            required: true
            description: Local warning ID or linked Kobo submission ID.
          - name: body
            in: body
            required: true
            schema:
              type: object
              additionalProperties: true
        responses:
          203:
            description: Warning updated successfully.
          400:
            description: The update could not be completed.
          401:
            description: A valid bearer token was not supplied.
        """
        
        try:
            response = update_submission(
                form_uid=form_uuid,
                submission_id=warn_id,
                submission_data=request.get_json() or {}
            )
            
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
@jwt_required(locations=['headers','cookies'])
def delete_warn(form_uuid: str, warn_id: str) :
        """Delete an existing Kobo-backed warning submission.
        ---
        tags:
          - Kobo submissions
        security:
          - BearerAuth: []
        parameters:
          - name: form_uuid
            in: path
            type: string
            required: true
            description: KoboToolbox asset UID for the survey form.
          - name: warn_id
            in: path
            type: string
            required: true
            description: Local warning ID or linked Kobo submission ID.
        responses:
          203:
            description: Warning deleted successfully.
          400:
            description: The deletion could not be completed.
          401:
            description: A valid bearer token was not supplied.
        """
        try:
            
            response=delete_submission(form_uuid=form_uuid,submission_id=warn_id)
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
  
