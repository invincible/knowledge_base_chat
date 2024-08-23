import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const AdminInterface = () => {
  const [nodes, setNodes] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchNodes();
  }, []);

  const fetchNodes = async () => {
    try {
      const response = await axios.get('/nodes');
      setNodes(response.data);
    } catch (error) {
      console.error('Error fetching nodes:', error);
    }
  };

  const handleNodeClick = async (nodeId) => {
    try {
      const response = await axios.get(`/node/${nodeId}`);
      const nodeData = response.data;
      setSelectedNode(nodeData);
      console.log('Selected node:', nodeData); // Добавим для отладки
    } catch (error) {
      console.error('Error fetching node:', error);
    }
  };

  const handleSave = async () => {
    if (!selectedNode) return;
    try {
      await axios.put(`/node/${selectedNode.id}`, {
        name: selectedNode.name,
        response: selectedNode.response
      });
      alert('Узел успешно обновлен');
      fetchNodes(); // Refresh the list of nodes
    } catch (error) {
      console.error('Error updating node:', error);
      alert('Failed to update node');
    }
  };

  return (
    <div className="admin-interface">
      <h1>Интерфейс администратора</h1>
      <button onClick={() => navigate('/')}>Вернуться в чат</button>
      <div style={{ display: 'flex' }}>
        <div style={{ width: '30%', marginRight: '20px' }}>
          {nodes.map(node => (
            <button
              key={node.id}
              onClick={() => handleNodeClick(node.id)}
              style={{ display: 'block', margin: '5px 0' }}
            >
              {node.name}
            </button>
          ))}
        </div>
        <div style={{ width: '70%' }}>
          {selectedNode && (
            <div>
              <input
                value={selectedNode.name || ''}
                onChange={(e) => setSelectedNode({...selectedNode, name: e.target.value})}
                style={{ width: '100%', marginBottom: '10px' }}
              />
              <textarea
                value={selectedNode.response || ''}
                onChange={(e) => setSelectedNode({...selectedNode, response: e.target.value})}
                style={{ width: '100%', height: '200px', marginBottom: '10px' }}
              />
              <button onClick={handleSave}>Сохранить</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminInterface;