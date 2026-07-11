import { useState } from 'react';
import { UploadCloud, FileText, CheckCircle } from 'lucide-react';

export default function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    // Simulate upload
    setTimeout(() => {
      setIsUploading(false);
      alert('Upload successful. Report is being processed.');
    }, 2000);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-slate-900">Patient Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Upload Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <UploadCloud className="text-primary-600" />
            Upload Medical Report
          </h2>
          
          <div 
            className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center hover:bg-slate-50 transition-colors cursor-pointer"
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleFileDrop}
            onClick={() => document.getElementById('fileUpload')?.click()}
          >
            <input 
              type="file" 
              id="fileUpload" 
              className="hidden" 
              accept=".pdf,.png,.jpg,.jpeg,.docx"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
            {file ? (
              <div className="flex flex-col items-center">
                <FileText className="h-12 w-12 text-primary-500 mb-2" />
                <p className="font-medium text-slate-700">{file.name}</p>
                <p className="text-sm text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            ) : (
              <div>
                <UploadCloud className="h-12 w-12 text-slate-400 mx-auto mb-2" />
                <p className="font-medium text-slate-700">Drag & drop your report here</p>
                <p className="text-sm text-slate-500">or click to browse</p>
                <p className="text-xs text-slate-400 mt-2">Supports PDF, PNG, JPG, DOCX</p>
              </div>
            )}
          </div>
          
          <button 
            onClick={handleUpload}
            disabled={!file || isUploading}
            className={`mt-4 w-full py-2 px-4 rounded-lg font-medium transition-colors ${
              file && !isUploading 
                ? 'bg-primary-600 hover:bg-primary-700 text-white shadow-sm' 
                : 'bg-slate-100 text-slate-400 cursor-not-allowed'
            }`}
          >
            {isUploading ? 'Uploading...' : 'Process Report'}
          </button>
        </div>

        {/* Recent Reports Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <FileText className="text-primary-600" />
            Recent Reports
          </h2>
          
          <div className="space-y-3">
            {[1, 2].map((i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg border border-slate-100 hover:bg-slate-50 transition-colors">
                <FileText className="h-5 w-5 text-slate-400 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-medium text-slate-900">Blood_Test_Results_2026.pdf</h3>
                  <p className="text-sm text-slate-500">Analyzed on July 9, 2026</p>
                </div>
                <CheckCircle className="h-5 w-5 text-emerald-500" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
