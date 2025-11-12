import React, { useState, useEffect } from 'react';
import { Calendar, Settings, ChevronRight, GripVertical } from 'lucide-react';

const WorkOrderGanttView = () => {
  const [workstations, setWorkstations] = useState([
    {
      id: 'ws1',
      name: 'Dyeing Unit',
      color: '#FF6B6B',
      workOrders: [
        { id: 'wo1', name: 'ALMN', item: 'Fabric A', start: 29, duration: 3 },
        { id: 'wo2', name: 'FINISH-23', item: 'Product B', start: 23, duration: 2 }
      ]
    },
    {
      id: 'ws2',
      name: 'Weaving',
      color: '#4ECDC4',
      workOrders: [
        { id: 'wo3', name: 'MBOOKS', item: 'Books', start: 15, duration: 5 },
        { id: 'wo4', name: 'GERP PRODUCT', item: 'Product C', start: 21, duration: 4 }
      ]
    },
    {
      id: 'ws3',
      name: 'Finishing',
      color: '#45B7D1',
      workOrders: [
        { id: 'wo5', name: 'CARPET-001', item: 'Carpet', start: 7, duration: 6 }
      ]
    },
    {
      id: 'ws4',
      name: 'Packing',
      color: '#95A5A6',
      workOrders: []
    }
  ]);

  const [draggedItem, setDraggedItem] = useState(null);
  const [draggedFrom, setDraggedFrom] = useState(null);

  // Generate date headers (October dates)
  const dates = Array.from({ length: 31 }, (_, i) => i + 1);

  const handleDragStart = (e, workOrder, workstationId) => {
    setDraggedItem(workOrder);
    setDraggedFrom(workstationId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, targetWorkstationId) => {
    e.preventDefault();
    
    if (!draggedItem || !draggedFrom) return;

    // Remove from source
    const newWorkstations = workstations.map(ws => {
      if (ws.id === draggedFrom) {
        return {
          ...ws,
          workOrders: ws.workOrders.filter(wo => wo.id !== draggedItem.id)
        };
      }
      if (ws.id === targetWorkstationId) {
        return {
          ...ws,
          workOrders: [...ws.workOrders, draggedItem]
        };
      }
      return ws;
    });

    setWorkstations(newWorkstations);
    setDraggedItem(null);
    setDraggedFrom(null);
  };

  const handleWorkOrderDrag = (e, workOrder, workstationId) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const dayWidth = rect.width / 31;
    const newStart = Math.floor(x / dayWidth) + 1;
    
    const newWorkstations = workstations.map(ws => {
      if (ws.id === workstationId) {
        return {
          ...ws,
          workOrders: ws.workOrders.map(wo => 
            wo.id === workOrder.id ? { ...wo, start: Math.max(1, Math.min(31 - wo.duration, newStart)) } : wo
          )
        };
      }
      return ws;
    });
    
    setWorkstations(newWorkstations);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              <h1 className="text-xl font-semibold text-gray-800">Work Order Schedule - October 2025</h1>
            </div>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Create Job Card
            </button>
          </div>
        </div>

        {/* Gantt Chart */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {/* Date Headers */}
          <div className="flex border-b bg-gray-50">
            <div className="w-48 flex-shrink-0 px-4 py-3 font-semibold text-gray-700 border-r">
              Workstation
            </div>
            <div className="flex-1 flex">
              {dates.map(date => (
                <div 
                  key={date} 
                  className="flex-1 text-center py-3 text-xs font-medium text-gray-600 border-r border-gray-200"
                >
                  {date}
                </div>
              ))}
            </div>
          </div>

          {/* Workstation Rows */}
          {workstations.map((workstation) => (
            <div 
              key={workstation.id}
              className="flex border-b hover:bg-gray-50 transition-colors"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, workstation.id)}
            >
              {/* Workstation Name */}
              <div className="w-48 flex-shrink-0 px-4 py-6 border-r bg-white">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: workstation.color }}
                  />
                  <span className="font-medium text-gray-800">{workstation.name}</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {workstation.workOrders.length} Work Orders
                </div>
              </div>

              {/* Timeline Grid */}
              <div className="flex-1 relative bg-white">
                {/* Grid lines */}
                <div className="absolute inset-0 flex">
                  {dates.map(date => (
                    <div key={date} className="flex-1 border-r border-gray-100" />
                  ))}
                </div>

                {/* Work Orders */}
                <div className="relative h-20 py-2">
                  {workstation.workOrders.map((wo) => (
                    <div
                      key={wo.id}
                      draggable
                      onDragStart={(e) => handleDragStart(e, wo, workstation.id)}
                      className="absolute h-12 rounded-lg shadow-md cursor-move hover:shadow-lg transition-all group"
                      style={{
                        backgroundColor: workstation.color,
                        left: `${((wo.start - 1) / 31) * 100}%`,
                        width: `${(wo.duration / 31) * 100}%`,
                        top: '8px'
                      }}
                    >
                      <div className="flex items-center h-full px-3 text-white">
                        <GripVertical className="w-4 h-4 mr-2 opacity-0 group-hover:opacity-100 transition-opacity" />
                        <div className="flex-1 overflow-hidden">
                          <div className="font-semibold text-sm truncate">{wo.name}</div>
                          <div className="text-xs opacity-90 truncate">{wo.item}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Instructions */}
        <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Settings className="w-5 h-5 text-blue-600 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-blue-900 mb-2">How to use:</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• <strong>Drag & Drop</strong> work orders between workstations</li>
                <li>• <strong>Click & Drag</strong> horizontally to change dates</li>
                <li>• Colors represent different workstations</li>
                <li>• Empty rows accept new work orders</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkOrderGanttView;