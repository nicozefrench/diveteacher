import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, CheckCircle, XCircle, Loader } from 'lucide-react'

export default function FileUpload({ onUploadComplete }) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState(null)

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setUploading(true)
    setProgress(0)
    setStatus({ type: 'uploading', message: 'Uploading...' })

    try {
      // Upload file
      const formData = new FormData()
      formData.append('file', file)

      const uploadResponse = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })

      if (!uploadResponse.ok) {
        throw new Error('Upload failed')
      }

      const { upload_id, filename } = await uploadResponse.json()
      
      setStatus({ type: 'processing', message: 'Processing document...' })
      setProgress(50)

      // Poll for processing status
      const pollStatus = async () => {
        const statusResponse = await fetch(`/api/upload/status/${upload_id}`)
        const statusData = await statusResponse.json()

        setProgress(statusData.progress || 50)

        if (statusData.status === 'completed') {
          setStatus({ type: 'success', message: 'Document processed!' })
          setProgress(100)
          onUploadComplete(upload_id, filename)
          setTimeout(() => {
            setUploading(false)
            setStatus(null)
          }, 2000)
        } else if (statusData.status === 'failed') {
          setStatus({ type: 'error', message: statusData.error || 'Processing failed' })
          setUploading(false)
        } else {
          setTimeout(pollStatus, 1000)
        }
      }

      pollStatus()

    } catch (error) {
      setStatus({ type: 'error', message: error.message })
      setUploading(false)
    }
  }, [onUploadComplete])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.ms-powerpoint': ['.ppt'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
    },
    multiple: false,
    disabled: uploading,
  })

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Upload Document</h2>
      
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        
        {isDragActive ? (
          <p className="text-blue-600 font-medium">Drop the file here...</p>
        ) : (
          <>
            <p className="text-gray-700 font-medium">
              Drag & drop a document, or click to select
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Supports PDF, PPT, PPTX (max 50MB)
            </p>
          </>
        )}
      </div>

      {/* Status */}
      {status && (
        <div className={`
          p-4 rounded-lg flex items-center gap-3
          ${status.type === 'success' ? 'bg-green-50 text-green-800' : ''}
          ${status.type === 'error' ? 'bg-red-50 text-red-800' : ''}
          ${status.type === 'uploading' || status.type === 'processing' ? 'bg-blue-50 text-blue-800' : ''}
        `}>
          {status.type === 'success' && <CheckCircle className="h-5 w-5" />}
          {status.type === 'error' && <XCircle className="h-5 w-5" />}
          {(status.type === 'uploading' || status.type === 'processing') && (
            <Loader className="h-5 w-5 animate-spin" />
          )}
          <span className="font-medium">{status.message}</span>
        </div>
      )}

      {/* Progress Bar */}
      {uploading && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  )
}

