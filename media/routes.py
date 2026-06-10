from flask import Blueprint,request
from utils.api_response import api_response
from media.services import upload_to_cloudinary
from media.models import MediaFile
from extensions import db
uploads_bp=Blueprint('uploads',__name__)

@uploads_bp.route('/',methods=['POST'])
@uploads_bp.route('',methods=['POST'])
def upload_file():
    try:
        #upload logic
        file=request.files.get("file")
        print('file',file)
        uploaded= upload_to_cloudinary(file)
        new_media_file=MediaFile(
            submission_id=None,
            question_name=None,
            filename=uploaded.get("filename"),
            original_filename=uploaded.get("originalName"),
            file_type=uploaded.get("type"),
            mime_type=uploaded.get("mimeType"),
            file_size=uploaded.get("size"),
            provider="cloudinary",
            public_id=uploaded.get("publicId"),
            file_path=uploaded.get("publicId"),
            url=uploaded.get("url"),
            optimized_url=uploaded.get("optimizedUrl"),
            width=uploaded.get("width"),
            height=uploaded.get("height"),
            duration=uploaded.get("duration"),
            format=uploaded.get("format"),
            upload_status="orphan"
        )
        db.session.add(new_media_file)
        db.session.commit()

        return api_response(
            success=True,
            data=new_media_file.to_dict(),
            message="File uploaded successfuly",
            status_code=200,
        )
    except ValueError as error:
        print(f"upload error {error}")
        return api_response(
            success=False,
            message=str(error),
            status_code=400
        )
    except Exception as e:
        print(f"file upload failed with error",e)
        return  api_response(
            success=False,
            message="File upload Failed.",
            status_code=500
        )