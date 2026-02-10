import React, { useState } from 'react';
import { Send, CheckCircle, AlertCircle } from 'lucide-react';
import { submitSingleFeedback } from '../services/api';
import StatusBadge from '../components/StatusBadge';

const UploadSingle: React.FC = () => {
  const [text, setText] = useState('');
  const [source, setSource] = useState('manual');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await submitSingleFeedback({ text, source });
      setResult(data);
      console.log('Verification: Single Ingestion Flow Complete', data);
    } catch (err: any) {
      setError(err.message || 'Failed to submit feedback');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Single Feedback Entry</h2>
        <p className="text-gray-500">Submit an individual customer voice for real-time classification.</p>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm border space-y-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Feedback Text</label>
            <textarea
              className="w-full h-32 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
              placeholder="Paste customer comment here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              required
            />
          </div>

          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">Source Context</label>
              <select 
                className="w-full px-4 py-2 border rounded-lg outline-none"
                value={source}
                onChange={(e) => setSource(e.target.value)}
              >
                <option value="manual">Manual Entry</option>
                <option value="youtube">YouTube Comment</option>
                <option value="reddit">Reddit Thread</option>
                <option value="twitter">X / Twitter</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                type="submit"
                disabled={loading || !text}
                className="flex items-center justify-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition min-w-[140px]"
              >
                {loading ? 'Processing...' : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Classify
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {error && (
          <div className="p-4 bg-rose-50 border border-rose-100 rounded-lg flex items-center text-rose-600">
            <AlertCircle className="w-5 h-5 mr-2" />
            {error}
          </div>
        )}

        {result && (
          <div className="animate-in fade-in slide-in-from-top-4 duration-500 border-t pt-6">
            <div className="flex items-center text-emerald-600 mb-4">
              <CheckCircle className="w-5 h-5 mr-2" />
              <span className="font-semibold text-sm">LLM Classification Successful</span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Identified Entity</h4>
                <div className="bg-gray-50 p-4 rounded-lg space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-gray-500">Company:</span> <span className="font-bold">{result.product_info.make}</span></div>
                  <div className="flex justify-between"><span className="text-gray-500">Model:</span> <span className="font-bold">{result.product_info.model}</span></div>
                  <div className="flex justify-between"><span className="text-gray-500">Category:</span> <span className="font-bold">{result.product_info.category}</span></div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Sentiment & Tone</h4>
                <div className="bg-gray-50 p-4 rounded-lg flex items-center justify-between">
                  <span className="text-sm text-gray-500">Primary Disposition:</span>
                  <StatusBadge status={result.sentiment} type="sentiment" />
                </div>
              </div>
            </div>

            <div className="mt-6">
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">AI Summary / Note</h4>
              <p className="text-sm bg-blue-50 p-4 rounded-lg text-blue-800 border border-blue-100 italic">
                "{result.annotator_note}"
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadSingle;
