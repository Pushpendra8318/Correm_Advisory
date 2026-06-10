import { useCallback, useRef, useState } from 'react'
import { CloudUpload, FileText, X, AlertCircle } from 'lucide-react'

export default function UploadCard({ onUpload, loading, progress, error, onClearError }) {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [fileError, setFileError] = useState(null)
  const inputRef = useRef(null)

  const handleFile = useCallback((file) => {
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setFileError(`"${file.name}" is not a PDF. Please upload an HDFC Bank statement in PDF format.`)
      return
    }
    if (file.size > 20 * 1024 * 1024) {
      setFileError('File is too large (max 20 MB). Please upload a smaller PDF.')
      return
    }
    setFileError(null)
    setSelectedFile(file)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragActive(false)
    const file = e.dataTransfer.files?.[0]
    handleFile(file)
  }, [handleFile])

  const handleDragOver = (e) => { e.preventDefault(); setDragActive(true) }
  const handleDragLeave = () => setDragActive(false)

  const handleInputChange = (e) => {
    handleFile(e.target.files?.[0])
  }

  const handleSubmit = () => {
    if (selectedFile && !loading) {
      onUpload(selectedFile)
    }
  }

  const handleClear = (e) => {
    e.stopPropagation()
    setSelectedFile(null)
    setFileError(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div className="w-full max-w-2xl mx-auto animate-slide-up">
      {/* Drop Zone */}
      <div
        className={`relative border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200
          ${dragActive
            ? 'border-brand bg-brand/10 scale-[1.01]'
            : 'border-white/20 hover:border-brand/60 hover:bg-white/5'
          }
          ${selectedFile ? 'border-emerald-500/50 bg-emerald-500/5' : ''}
        `}
        onClick={() => !selectedFile && inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={handleInputChange}
        />

        {selectedFile ? (
          <div className="flex items-center justify-center gap-4 animate-fade-in">
            <div className="flex items-center justify-center w-14 h-14 rounded-xl bg-emerald-500/20 border border-emerald-500/30">
              <FileText className="w-7 h-7 text-emerald-400" />
            </div>
            <div className="text-left flex-1 min-w-0">
              <p className="font-semibold text-white truncate">{selectedFile.name}</p>
              <p className="text-sm text-slate-400 mt-0.5">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button
              onClick={handleClear}
              className="p-2 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4">
            <div className={`flex items-center justify-center w-16 h-16 rounded-2xl border-2
              ${dragActive ? 'bg-brand/20 border-brand' : 'bg-white/5 border-white/20'} transition-colors`}>
              <CloudUpload className={`w-8 h-8 ${dragActive ? 'text-brand' : 'text-slate-400'}`} />
            </div>
            <div>
              <p className="text-base font-medium text-white">
                Drop your HDFC Bank statement here
              </p>
              <p className="text-sm text-slate-400 mt-1">
                or <span className="text-brand font-medium cursor-pointer hover:underline">click to browse</span>
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="px-2 py-0.5 rounded border border-white/10 bg-white/5">PDF only</span>
              <span className="px-2 py-0.5 rounded border border-white/10 bg-white/5">HDFC Bank</span>
              <span className="px-2 py-0.5 rounded border border-white/10 bg-white/5">Max 20MB</span>
            </div>
          </div>
        )}
      </div>

      {/* File-type / size error */}
      {fileError && (
        <div className="mt-3 flex items-start gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 animate-fade-in">
          <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-amber-300">Invalid file</p>
            <p className="text-sm text-amber-400/80 mt-0.5">{fileError}</p>
          </div>
          <button onClick={() => setFileError(null)} className="text-amber-400 hover:text-amber-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Backend error */}
      {error && (
        <div className="mt-3 flex items-start gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/30 animate-fade-in">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-red-300">Processing failed</p>
            <p className="text-sm text-red-400/80 mt-0.5">{error}</p>
          </div>
          <button onClick={onClearError} className="text-red-400 hover:text-red-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Progress */}
      {loading && (
        <div className="mt-4 space-y-2 animate-fade-in">
          <div className="flex justify-between text-xs text-slate-400 mb-1">
            <span>{progress < 40 ? 'Uploading…' : progress < 80 ? 'Parsing transactions…' : 'Building report…'}</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-brand to-blue-400 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Submit Button */}
      {selectedFile && !loading && (
        <button
          onClick={handleSubmit}
          className="btn-primary w-full mt-4 py-4 text-base animate-slide-up"
        >
          <CloudUpload className="w-5 h-5" />
          Analyze Statement
        </button>
      )}
    </div>
  )
}
