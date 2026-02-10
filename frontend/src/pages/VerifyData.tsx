import React, { useEffect, useState } from 'react';
import { ShieldCheck, Search, Filter, RefreshCcw, Table as TableIcon, LayoutGrid } from 'lucide-react';
import { getClassifiedFeedback } from '../services/api';
import StatusBadge from '../components/StatusBadge';

const VerifyData: React.FC = () => {
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState<'grid' | 'table'>('table');
    const [searchTerm, setSearchTerm] = useState('');

    const fetchData = async () => {
        setLoading(true);
        try {
            const result = await getClassifiedFeedback();
            setData(result);
        } catch (error) {
            console.error('Failed to fetch audit data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const filteredData = data.filter(item => 
        (item.raw_text?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.make_brand?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.model?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.company_name?.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                        <ShieldCheck className="w-6 h-6 mr-2 text-blue-600" />
                        Verification View
                    </h2>
                    <p className="text-gray-500 text-sm">Review AI-derived insights and audit model accuracy.</p>
                </div>
                <div className="flex items-center space-x-2">
                    <button 
                        onClick={fetchData}
                        className="p-2 hover:bg-gray-100 rounded-lg transition"
                        title="Refresh Data"
                    >
                        <RefreshCcw className={`w-5 h-5 text-gray-500 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                    <div className="flex border rounded-lg overflow-hidden bg-white">
                        <button 
                            onClick={() => setViewMode('table')}
                            className={`p-2 ${viewMode === 'table' ? 'bg-gray-100 text-blue-600' : 'text-gray-400'}`}
                        >
                            <TableIcon className="w-5 h-5" />
                        </button>
                        <button 
                            onClick={() => setViewMode('grid')}
                            className={`p-2 ${viewMode === 'grid' ? 'bg-gray-100 text-blue-600' : 'text-gray-400'}`}
                        >
                            <LayoutGrid className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>

            <div className="flex gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input 
                        type="text" 
                        placeholder="Search by keywords or company..."
                        className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <button className="flex items-center px-4 py-2 bg-white border rounded-lg hover:bg-gray-50 text-gray-600">
                    <Filter className="w-4 h-4 mr-2" />
                    Advanced Filters
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <div className="animate-pulse text-gray-400 flex flex-col items-center">
                        <Loader2 className="w-10 h-10 animate-spin mb-2" />
                        Loading classified records...
                    </div>
                </div>
            ) : filteredData.length === 0 ? (
                <div className="text-center py-20 bg-gray-50 rounded-xl border border-dashed text-gray-400">
                    No records found matching your query.
                </div>
            ) : viewMode === 'table' ? (
                <div className="bg-white rounded-xl shadow-sm border overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest min-w-[300px]">Feedback</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest min-w-[150px]">Brand/Model</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest min-w-[150px]">Classification</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest min-w-[100px]">Sentiment</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest min-w-[200px]">Dispositions 1-5</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest min-w-[180px]">Product Attributes</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest min-w-[180px]">Purchase Context</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {filteredData.map((item, idx) => (
                                <tr key={item.id || idx} className="hover:bg-blue-50 transition">
                                    <td className="px-6 py-4">
                                        <div className="line-clamp-3 text-sm text-gray-700 font-medium">
                                            "{item.raw_text}"
                                        </div>
                                        <div className="flex items-center gap-2 mt-2">
                                            <span className="text-[10px] text-gray-400 uppercase px-1.5 py-0.5 bg-gray-100 rounded">{item.source}</span>
                                            {item.item_id && <span className="text-[10px] text-blue-500 font-mono">ID: {item.item_id}</span>}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="text-xs">
                                            <p className="font-bold text-gray-900">{item.make_brand || '---'}</p>
                                            <p className="text-gray-500">{item.model || '---'}</p>
                                            <p className="text-[10px] text-gray-400 italic">{item.variant || ''}</p>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="text-xs">
                                            <p className="text-gray-900 font-medium">{item.product_category || '---'}</p>
                                            <p className="text-gray-500">{item.product_subcategory || '---'}</p>
                                            <span className="text-[10px] text-gray-400 italic block mt-1">{item.item_type || 'unspecified'}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <StatusBadge status={item.sentiment} type="sentiment" />
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex flex-wrap gap-1 max-w-[250px]">
                                            {item.disposition_1 && <span className="text-[9px] bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded border border-blue-100">{item.disposition_1}</span>}
                                            {item.disposition_2 && <span className="text-[9px] bg-indigo-50 text-indigo-600 px-1.5 py-0.5 rounded border border-indigo-100">{item.disposition_2}</span>}
                                            {item.disposition_3 && <span className="text-[9px] bg-purple-50 text-purple-600 px-1.5 py-0.5 rounded border border-purple-100">{item.disposition_3}</span>}
                                            {item.disposition_4 && <span className="text-[9px] bg-pink-50 text-pink-600 px-1.5 py-0.5 rounded border border-pink-100">{item.disposition_4}</span>}
                                            {item.disposition_5 && <span className="text-[9px] bg-gray-50 text-gray-600 px-1.5 py-0.5 rounded border border-gray-100">{item.disposition_5}</span>}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="text-[10px] text-gray-600 grid grid-cols-2 gap-x-2 gap-y-0.5">
                                            <span className="text-gray-400">Year:</span> <span>{item.release_year || '---'}</span>
                                            <span className="text-gray-400">Price:</span> <span>{item.price_band || '---'}</span>
                                            <span className="text-gray-400">Color:</span> <span>{item.color || '---'}</span>
                                            <span className="text-gray-400">Specs:</span> <span>{item.size_capacity || '---'}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="text-[10px] text-gray-600 space-y-0.5">
                                            <div className="flex justify-between"><span className="text-gray-400">Region:</span> <span>{item.purchase_region || '---'}</span></div>
                                            <div className="flex justify-between"><span className="text-gray-400">Usage:</span> <span>{item.usage_duration_bucket || '---'}</span></div>
                                            <div className="flex items-center gap-1 mt-1 font-bold">
                                                {item.verified_purchase ? 
                                                    <span className="text-emerald-500 font-bold uppercase text-[8px]">✓ Verified</span> : 
                                                    <span className="text-gray-400 uppercase text-[8px]">Unverified</span>
                                                }
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredData.map((item, idx) => (
                        <div key={item.id || idx} className="bg-white p-6 rounded-xl shadow-sm border hover:shadow-md transition">
                            <div className="flex justify-between items-start mb-4">
                                <StatusBadge status={item.sentiment} type="sentiment" />
                                <span className="text-xs text-gray-400">{new Date().toLocaleDateString()}</span>
                            </div>
                            <p className="text-gray-800 text-sm mb-6 font-medium line-clamp-4 italic border-l-4 border-blue-200 pl-4">
                                "{item.raw_text}"
                            </p>
                            <div className="flex items-center justify-between text-xs font-bold text-gray-400 uppercase tracking-widest mt-auto">
                                <span>{item.product_info.make}</span>
                                <span className="text-blue-600">Review Result</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

const Loader2 = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
);

export default VerifyData;
