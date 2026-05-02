import React from 'react';

interface SyncLog {
  id: number;
  platformName: string;
  action: string;
  status: 'pending' | 'success' | 'failed';
  errorMessage?: string;
  timestamp: string;
}

interface SyncStatusProps {
  logs: SyncLog[];
}

export const SyncStatus: React.FC<SyncStatusProps> = ({ logs }) => {
  return (
    <div className="bg-white shadow rounded-lg p-6 max-w-2xl w-full">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Integration Sync Status</h2>
      
      {logs.length === 0 ? (
        <p className="text-gray-500 italic">No sync activity yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Platform</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {logs.map((log) => (
                <tr key={log.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 capitalize">{log.platformName}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{log.action}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      log.status === 'success' ? 'bg-green-100 text-green-800' : 
                      log.status === 'failed' ? 'bg-red-100 text-red-800' : 
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {log.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(log.timestamp).toLocaleTimeString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
