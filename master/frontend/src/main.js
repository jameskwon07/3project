// Master Frontend - Agent 관리 인터페이스
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

// DOM 요소
const agentsList = document.getElementById('agents-list');
const healthStatus = document.getElementById('health-status');
const agentCount = document.getElementById('agent-count');

// 상태 업데이트
async function updateHealth() {
    try {
        const response = await axios.get(`${API_BASE}/health`);
        healthStatus.className = 'status-indicator healthy';
        healthStatus.textContent = '● Healthy';
        agentCount.textContent = `Agents: ${response.data.agents_count}`;
    } catch (error) {
        healthStatus.className = 'status-indicator error';
        healthStatus.textContent = '● Error';
        console.error('Health check failed:', error);
    }
}

// Agent 목록 로드
async function loadAgents() {
    try {
        const response = await axios.get(`${API_BASE}/agents`);
        displayAgents(response.data);
    } catch (error) {
        console.error('Failed to load agents:', error);
        agentsList.innerHTML = '<p class="error">Failed to load agents</p>';
    }
}

// Agent 목록 표시
function displayAgents(agents) {
    if (agents.length === 0) {
        agentsList.innerHTML = '<p class="empty">No agents registered</p>';
        return;
    }

    agentsList.innerHTML = agents.map(agent => `
        <div class="agent-card ${agent.status}">
            <div class="agent-header">
                <h3>${agent.name}</h3>
                <span class="platform-badge ${agent.platform}">${agent.platform}</span>
            </div>
            <div class="agent-info">
                <p><strong>Version:</strong> ${agent.version}</p>
                <p><strong>Status:</strong> <span class="status-badge ${agent.status}">${agent.status}</span></p>
                <p><strong>Last Seen:</strong> ${new Date(agent.last_seen).toLocaleString()}</p>
                ${agent.ip_address ? `<p><strong>IP:</strong> ${agent.ip_address}</p>` : ''}
            </div>
        </div>
    `).join('');
}

// 초기화
async function init() {
    await updateHealth();
    await loadAgents();
    
    // 주기적으로 업데이트 (5초마다)
    setInterval(async () => {
        await updateHealth();
        await loadAgents();
    }, 5000);
}

init();

