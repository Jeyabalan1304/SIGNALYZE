import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { uploadCSV } from '../services/api';

const UploadCSV: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [status, setStatus] = useState<'idle' | 'uploading' | 'completed' | 'error'>('idle');
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<any>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setStatus('idle');
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setStatus('uploading');
        setError(null);

        try {
            const data = await uploadCSV(file);
            setResult(data);
            setStatus('completed');
        } catch (err: any) {
            setError(err.message || 'CSV processing failed');
            setStatus('error');
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div>
                <h2 className="text-2xl font-bold text-gray-900">Bulk Ingestion</h2>
                <p className="text-gray-500">Upload CSV files containing customer feedback for batch processing.</p>
            </div>

            <div className="bg-white p-10 rounded-xl shadow-sm border border-dashed border-gray-300 flex flex-col items-center justify-center text-center">
                {!file ? (
                    <div className="space-y-4">
                        <div className="bg-blue-50 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto">
                            <Upload className="w-8 h-8 text-blue-600" />
                        </div>
                        <div>
                            <label className="cursor-pointer">
                                <span className="text-blue-600 font-semibold hover:underline">Click to upload</span> or drag and drop
                                <input type="file" className="hidden" accept=".csv" onChange={handleFileChange} />
                            </label>
                            <p className="text-xs text-gray-400 mt-1">Requires 'text' and 'source' columns</p>
                        </div>
                    </div>
                ) : (
                    <div className="w-full space-y-6">
                        <div className="flex items-center justify-center space-x-3 bg-gray-50 p-4 rounded-lg">
                            <FileText className="w-6 h-6 text-gray-400" />
                            <div className="text-left">
                                <p className="text-sm font-medium text-gray-900">{file.name}</p>
                                <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(2)} KB</p>
                            </div>
                            <button 
                                onClick={() => setFile(null)}
                                className="text-xs text-rose-600 hover:underline px-4"
                            >
                                Remove
                            </button>
                        </div>

                        {status === 'idle' && (
                            <button
                                onClick={handleUpload}
                                className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                            >
                                Process CSV
                            </button>
                        )}

                        {status === 'uploading' && (
                            <div className="flex flex-col items-center space-y-3">
                                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                                <p className="text-sm font-medium text-gray-600">Analyzing feedback patterns...</p>
                            </div>
                        )}

                        {status === 'completed' && (
                            <div className="bg-emerald-50 border border-emerald-100 p-6 rounded-lg text-emerald-800">
                                <div className="flex items-center justify-center mb-4">
                                    <CheckCircle className="w-10 h-10 mr-2" />
                                    <h3 className="text-xl font-bold">Successfully Ingested</h3>
                                </div>
                                <div className="grid grid-cols-2 gap-4 text-center">
                                    <div className="bg-white p-3 rounded shadow-sm">
                                        <p className="text-2xl font-bold">{result?.count || 0}</p>
                                        <p className="text-xs text-gray-500 uppercase">Records Processed</p>
                                    </div>
                                    <div className="bg-white p-3 rounded shadow-sm">
                                        <p className="text-2xl font-bold">Queued</p>
                                        <p className="text-xs text-gray-500 uppercase">Status</p>
                                    </div>
                                </div>
                                <p className="text-sm mt-4 italic opacity-75">Pipelines are now running in the background. Check Verification view for updates.</p>
                            </div>
                        )}

                        {status === 'error' && (
                            <div className="bg-rose-50 border border-rose-100 p-6 rounded-lg text-rose-800 flex items-center">
                                <AlertCircle className="w-8 h-8 mr-4" />
                                <div className="text-left">
                                    <h3 className="font-bold">Error Processing File</h3>
                                    <p className="text-sm">{error}</p>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default UploadCSV;
