import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';
import { UPLOAD_MAX_FILE_SIZE_MB, SUPPORTED_FILE_TYPES } from '../../config/brand';
import { Button } from '../ui/Button';

const DocumentUpload = ({ onFileSelect, isUploading }) => {
  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.ms-powerpoint': ['.ppt'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
    },
    maxSize: UPLOAD_MAX_FILE_SIZE_MB * 1024 * 1024,
    multiple: false,
    disabled: isUploading,
  });

  return (
    <div>
      <div
        {...getRootProps()}
        className={cn(
          "relative cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-all duration-200",
          isDragActive && !isDragReject && "border-primary-400 bg-primary-50",
          isDragReject && "border-error-400 bg-error-50",
          !isDragActive && !isDragReject && "border-gray-300 hover:border-gray-400 hover:bg-gray-50",
          isUploading && "pointer-events-none opacity-50"
        )}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center gap-3">
          {isUploading ? (
            <>
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary-100">
                <Loader2 className="h-6 w-6 animate-spin text-primary-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Uploading...</p>
                <p className="mt-1 text-xs text-gray-500">Please wait while your document is uploaded</p>
              </div>
            </>
          ) : isDragActive ? (
            <>
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary-100">
                <Upload className="h-6 w-6 text-primary-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Drop your file here</p>
                <p className="mt-1 text-xs text-gray-500">Release to upload</p>
              </div>
            </>
          ) : (
            <>
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
                <FileText className="h-6 w-6 text-gray-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Drag & drop a file here
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  or click to browse
                </p>
              </div>
              <Button
                type="button"
                variant="primary"
                size="sm"
                className="mt-2"
              >
                <Upload className="h-4 w-4" />
                Select File
              </Button>
              <p className="mt-3 text-xs text-gray-500">
                {SUPPORTED_FILE_TYPES.join(', ')} • Max {UPLOAD_MAX_FILE_SIZE_MB}MB
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;
