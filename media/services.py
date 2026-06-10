import cloudinary 
from cloudinary.uploader import upload,upload_large
from cloudinary.utils import cloudinary_url
import uuid
import os 
import mimetypes
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif","image/heic", "image/heif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}
ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

MAX_IMAGE_SIZE = 100 * 1024 * 1024       # 10MB
MAX_VIDEO_SIZE = 450 * 1024 * 1024      # 100MB
MAX_DOCUMENT_SIZE = 20 * 1024 * 1024    # 20MB


config=cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def get_file_size(file:FileStorage)->int:
    file.stream.seek(0,os.SEEK_END)
    size=file.stream.tell()
    file.stream.seek(0)
    return size

def detect_file_type(mime_type:str)->str:
    if mime_type in ALLOWED_IMAGE_TYPES:
        return "image"
    if mime_type in ALLOWED_VIDEO_TYPES:
        return "video"
    if mime_type in ALLOWED_DOCUMENT_TYPES:
        return "document"
    
    raise ValueError (f"Unsupported file type : {mime_type}")

def validate_file(file:FileStorage):
    if not file:
        raise ValueError("No file provided.")
    if not file.filename:
        raise ValueError("File must have a filename.")

    filename=secure_filename(file.filename)
    mime_type=file.mimetype or mimetypes.guess_type(filename)[0]
    if not mime_type:
        raise ValueError("Could not detect file type.")
    file_type = detect_file_type(mime_type)
    file_size = get_file_size(file)

    if file_type == "image" and file_size > MAX_IMAGE_SIZE:
        raise ValueError(f"Image is too large. Maximum size is {MAX_IMAGE_SIZE}")

    if file_type == "video" and file_size > MAX_VIDEO_SIZE:
        raise ValueError(f"Video is too large. Maximum size is {MAX_IMAGE_SIZE}")
    if file_type == "document" and file_size > MAX_DOCUMENT_SIZE:
        raise ValueError(f"Document is too large. Maximum size is {MAX_DOCUMENT_SIZE}")
    return {
        "filename":filename,
        "mime_type":mime_type,
        "file_type":file_type,
        "size":file_size
    }

def upload_to_cloudinary(
    file: FileStorage,
    folder: str = "wildlife-warning-app/uploads",
    user_id: str | None = None,
):
    metadata = validate_file(file)

    file_type = metadata["file_type"]
    filename_without_ext = os.path.splitext(metadata["filename"])[0]

    public_id = f"{folder}/{user_id or 'anonymous'}/{uuid.uuid4()}-{filename_without_ext}"

    if file_type == "image":
        resource_type = "image"

        upload_options = {
            "resource_type": resource_type,
            "public_id": public_id,
            "overwrite": False,
            "folder": folder,
            "transformation": [
                {"quality": "auto", "fetch_format": "auto"},
            ],
            "eager": [
                {
                    "width": 500,
                    "height": 500,
                    "crop": "fill",
                    "gravity": "auto",
                    "quality": "auto",
                    "fetch_format": "auto",
                },
                {
                    "width": 1200,
                    "crop": "limit",
                    "quality": "auto",
                    "fetch_format": "auto",
                },
            ],
        }

    elif file_type == "video":
        resource_type = "video"

        upload_options = {
            "resource_type": resource_type,
            "public_id": public_id,
            "overwrite": False,
            "folder": folder,
            "eager": [
                {
                    "width": 720,
                    "height": 720,
                    "crop": "limit",
                    "quality": "auto",
                    "format": "mp4",
                }
            ],
            "eager_async": True,
        }

    else:
        resource_type = "raw"

        upload_options = {
            "resource_type": resource_type,
            "public_id": public_id,
            "overwrite": False,
            "folder": folder,
        }
    if file_type=='image':
        result = upload(file, **upload_options)
    elif file_type=="video":
        result=upload_large(file,**upload_options)
        

    optimized_url, _ = cloudinary_url(
        result["public_id"],
        resource_type=resource_type,
        secure=True,
        quality="auto" if file_type in ["image", "video"] else None,
        fetch_format="auto" if file_type == "image" else None,
    )

    return {
        "id": result.get("asset_id"),
        "publicId": result.get("public_id"),
        "url": result.get("secure_url"),
        "optimizedUrl": optimized_url,
        "resourceType": result.get("resource_type"),
        "type": file_type,
        "format": result.get("format"),
        "mimeType": metadata["mime_type"],
        "originalName": metadata["filename"],
        "filename":metadata["filename"],
        "size": result.get("bytes") or metadata["size"],
        "width": result.get("width"),
        "height": result.get("height"),
        "duration": result.get("duration"),
        "provider": "cloudinary",
        "createdAt": result.get("created_at"),
    }