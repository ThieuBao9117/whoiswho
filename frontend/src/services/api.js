import axios from 'axios';

// ---------------------------------------------------------
// FORCED DEMO MODE FLAG
// Set to true to bypass all backend communication for demo
// ---------------------------------------------------------
const IS_DEMO_MODE = true; 

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add token if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('csb_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ---------------------------------------------------------
// AGGRESSIVE DEMO MODE INTERCEPTOR
// Replaces real requests with mock responses for demonstration
// ---------------------------------------------------------
api.interceptors.request.use(async (config) => {
    if (!IS_DEMO_MODE) return config;

    console.log(`[DEMO MODE] Intercepting request: ${config.url}`);
    
    // Simulate network delay for demo feel
    await new Promise(r => setTimeout(r, 600));

    // Define mock data for all routes used in App.jsx
    const mockResponses = {
        '/auth/login': {
            data: { access_token: 'mock-demo-token-admin', token_type: 'bearer' }
        },
        '/auth/me': {
            data: {
                username: "demo_admin",
                is_staff: true, 
                employee_profile: {
                    id: 1, emp_code: "ADM-001", full_name: "Demo Admin (CSB)",
                    department: "HR Dept", role: "HR Manager", join_date: "2026-03-01",
                    photo: "https://i.pravatar.cc/150?u=admin"
                }
            }
        },
        '/connections/my': {
            data: [
                { id: 1, status: 'ACCEPTED', connector: { role: 'Operator' } },
                { id: 2, status: 'ACCEPTED', connector: { role: 'Leader' } },
                { id: 3, status: 'ACCEPTED', connector: { role: 'Part Leader' } },
                { id: 4, status: 'PENDING', connector: { role: 'Team Manager' } }
            ]
        },
        '/connectors/search': {
            data: [
                { id: 101, full_name: "Nguyễn Văn A (Leader)", department: "Sản xuất", role: "Leader" },
                { id: 102, full_name: "Lê Văn B (Part Leader)", department: "Kỹ thuật", role: "Part Leader" },
                { id: 103, full_name: "Trần Thị C (Manager)", department: "Sản xuất", role: "Team Manager" }
            ]
        },
        '/admin/leaderboard': {
            data: [
                { id: 'E1', name: "Hoàng Minh", dept: "Sản xuất", score: 12, avatar: "https://i.pravatar.cc/150?u=1", isTop: true },
                { id: 'E2', name: "Thu Hà", dept: "Marketing", score: 8, avatar: "https://i.pravatar.cc/150?u=2" },
                { id: 'E3', name: "Quốc Anh", dept: "Kỹ thuật", score: 5, avatar: "https://i.pravatar.cc/150?u=3" }
            ]
        },
        '/admin/stats/': { // Matches /admin/stats/2026-03 etc
            data: { total_employees: 48, completed_kpi: 32, projected_reward: 16000000, total_connections: 215 }
        },
        '/admin/report/': {
            data: [
                { emp_code: "EMP-001", full_name: "Hoàng Minh", department: "Sản xuất", count: "9/9", reward: 500000 },
                { emp_code: "ADM-001", full_name: "Demo Admin", department: "HR Dept", count: "5/9", reward: 0 }
            ]
        },
        '/targets/': {
            data: {
                period_str: "2026-03", operator_required: 5, leader_required: 2, 
                pl_required: 1, tm_required: 1, gd_required: 0, reward_amount: 500000
            }
        }
    };

    // Find a matching mock response
    const match = Object.keys(mockResponses).find(key => config.url.includes(key));

    if (match) {
        // Return a cancelled promise to bypass the actual request
        const response = {
            data: mockResponses[match].data, status: 200, statusText: 'OK', config, headers: {}
        };
        // Throwing an object that looks like a response to skip real networking
        throw { demoMode: true, response };
    }

    return config;
});

// Handle the "thrown" mock response in the response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.demoMode) return Promise.resolve(error.response);
    return Promise.reject(error);
  }
);

export default api;
