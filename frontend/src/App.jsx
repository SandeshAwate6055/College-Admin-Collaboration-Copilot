import React, { useState, useEffect } from 'react';
import { 
  BookOpen, Users, Award, FileText, Send, Search, Filter, 
  ExternalLink, CheckCircle, AlertCircle, Building, Briefcase, 
  Sparkles, ChevronRight, User, GraduationCap, ShieldCheck, Download
} from 'lucide-react';
import { marked } from 'marked';

export default function App() {
  const [activeTab, setActiveTab] = useState('knowledge'); // knowledge | talent | research | profile | tickets

  // Knowledge State
  const [chatMessages, setChatMessages] = useState([
    { role: 'bot', text: 'Hello! I am the **VIT Pune AI Copilot**. Ask me about examination policies, CGPA rules, summer term registration, scholarships, placements, or departments.' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatStudentId, setChatStudentId] = useState('12110452');
  const [chatLoading, setChatLoading] = useState(false);
  const [knowledgeData, setKnowledgeData] = useState(null);

  // Talent State
  const [talentStudents, setTalentStudents] = useState([]);
  const [talentTotal, setTalentTotal] = useState(0);
  const [talentLoading, setTalentLoading] = useState(false);
  const [filters, setFilters] = useState({
    q: '',
    branch: '',
    year: '',
    min_cgpa: '',
    domain: '',
    has_hackathon: false,
    has_internship: false,
  });
  const [roleRequirement, setRoleRequirement] = useState('');
  const [recommendations, setRecommendations] = useState(null);
  const [recommendLoading, setRecommendLoading] = useState(false);

  // Research State
  const [researchItems, setResearchItems] = useState([]);
  const [researchTotal, setResearchTotal] = useState(0);
  const [researchPapersTotal, setResearchPapersTotal] = useState(377);
  const [researchPatentsTotal, setResearchPatentsTotal] = useState(77);
  const [researchAvailableDomains, setResearchAvailableDomains] = useState([]);
  const [researchType, setResearchType] = useState('all');
  const [researchDomain, setResearchDomain] = useState('');
  const [researchQuery, setResearchQuery] = useState('');
  const [researchLoading, setResearchLoading] = useState(false);

  // Student 360 State
  const [targetPrn, setTargetPrn] = useState('12110452');
  const [student360Data, setStudent360Data] = useState(null);
  const [portfolioData, setPortfolioData] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);

  // Tickets State
  const [ticketStudentId, setTicketStudentId] = useState('12110452');
  const [ticketDescription, setTicketDescription] = useState('');
  const [ticketsList, setTicketsList] = useState([]);
  const [ticketSuccess, setTicketSuccess] = useState('');

  // Fetch initial knowledge overview
  useEffect(() => {
    fetch('/api/platform/knowledge/overview')
      .then(res => res.json())
      .then(data => setKnowledgeData(data))
      .catch(err => console.error(err));
  }, []);

  // Fetch Talent on filter changes
  useEffect(() => {
    if (activeTab === 'talent') {
      fetchTalent();
    }
  }, [activeTab, filters]);

  // Fetch Research items
  useEffect(() => {
    if (activeTab === 'research') {
      fetchResearch();
    }
  }, [activeTab, researchType, researchDomain, researchQuery]);

  const fetchTalent = async () => {
    setTalentLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.q) params.append('q', filters.q);
      if (filters.branch) params.append('branch', filters.branch);
      if (filters.year) params.append('year', filters.year);
      if (filters.min_cgpa) params.append('min_cgpa', filters.min_cgpa);
      if (filters.domain) params.append('domain', filters.domain);
      if (filters.has_hackathon) params.append('has_hackathon', 'true');
      if (filters.has_internship) params.append('has_internship', 'true');

      const res = await fetch(`/api/platform/talent/filter?${params.toString()}`);
      const data = await res.json();
      setTalentStudents(data.results || []);
      setTalentTotal(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setTalentLoading(false);
    }
  };

  const fetchResearch = async () => {
    setResearchLoading(true);
    try {
      const params = new URLSearchParams();
      if (researchQuery) params.append('q', researchQuery);
      if (researchType !== 'all') params.append('item_type', researchType);
      if (researchDomain) params.append('domain', researchDomain);

      const res = await fetch(`/api/platform/research/search?${params.toString()}`);
      const data = await res.json();
      setResearchItems(data.results || []);
      setResearchTotal(data.total || 0);
      if (data.total_papers) setResearchPapersTotal(data.total_papers);
      if (data.total_patents) setResearchPatentsTotal(data.total_patents);
      if (data.available_domains && data.available_domains.length > 0) {
        setResearchAvailableDomains(data.available_domains);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setResearchLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput;
    setChatMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setChatInput('');
    setChatLoading(true);

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: chatStudentId,
          message: userMsg
        })
      });
      const data = await res.json();
      let reply = data.answer || data.message || 'No response returned.';
      if (data.citations && data.citations.length > 0) {
        reply += '\n\n**Official Citations:**\n' + data.citations.map(c => `- *${c.source}* (Page ${c.page})`).join('\n');
      }
      if (data.ticket_id) {
        reply += `\n\n**Registered Support Ticket:** #${data.ticket_id}`;
      }
      setChatMessages(prev => [...prev, { role: 'bot', text: reply, raw: data }]);
    } catch (err) {
      setChatMessages(prev => [...prev, { role: 'bot', text: `Error: ${err.message}` }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleRecommendRole = async () => {
    if (!roleRequirement.trim()) return;
    setRecommendLoading(true);
    try {
      const res = await fetch('/api/intelligence/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          requirement: roleRequirement,
          top_k: 5,
          branch: filters.branch || '',
          year: filters.year || '',
          min_cgpa: filters.min_cgpa ? parseFloat(filters.min_cgpa) : null,
          domain: filters.domain || '',
        })
      });
      const data = await res.json();
      setRecommendations(data.recommendations || []);
    } catch (err) {
      console.error(err);
    } finally {
      setRecommendLoading(false);
    }
  };

  const loadStudentProfile = async (prn) => {
    setProfileLoading(true);
    setTargetPrn(prn);
    setActiveTab('profile');
    try {
      const res1 = await fetch(`/api/intelligence/student/${prn}`);
      const data1 = await res1.json();
      setStudent360Data(data1);

      const res2 = await fetch(`/api/intelligence/portfolio/${prn}`);
      const data2 = await res2.json();
      setPortfolioData(data2.portfolio);
    } catch (err) {
      console.error(err);
    } finally {
      setProfileLoading(false);
    }
  };

  const handleCreateTicket = async () => {
    if (!ticketDescription.trim()) return;
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: ticketStudentId,
          message: `Complaint: ${ticketDescription}`
        })
      });
      const data = await res.json();
      setTicketSuccess(`Complaint lodged successfully! Ticket ID: #${data.ticket_id}`);
      setTicketDescription('');
      fetchTickets();
    } catch (err) {
      console.error(err);
    }
  };

  const fetchTickets = async () => {
    try {
      const res = await fetch(`/tickets/${ticketStudentId}`);
      const data = await res.json();
      setTicketsList(data || []);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-100">
      {/* Institutional Top Header */}
      <header className="bg-vit-maroon text-white border-b-4 border-vit-gold shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-full bg-white p-1.5 flex items-center justify-center shadow-inner border-2 border-vit-gold overflow-hidden flex-shrink-0">
              <img 
                src="/vit_logo.png" 
                alt="Vishwakarma Institutes Logo" 
                className="w-full h-full object-contain"
              />
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-amber-200 font-medium">Bansilal Ramnath Agarwal Charitable Trust's</p>
              <h1 className="text-xl md:text-2xl font-bold tracking-tight">Vishwakarma Institute of Technology, Pune</h1>
              <p className="text-xs text-slate-200">An Autonomous Institute Affiliated to Savitribai Phule Pune University</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="bg-vit-maroonDark px-2.5 py-1 rounded-md border border-amber-400 text-amber-300 font-semibold">NAAC A++ Grade</span>
            <span className="bg-vit-maroonDark px-2.5 py-1 rounded-md border border-slate-400 text-slate-200">NBA Accredited</span>
            <span className="bg-vit-maroonDark px-2.5 py-1 rounded-md border border-slate-400 text-slate-200">Autonomous</span>
          </div>
        </div>

        {/* 3 Pillars Navigation matching Basic_Arch.jpeg */}
        <div className="bg-vit-maroonDark px-4 sm:px-6 lg:px-8 border-t border-red-950">
          <div className="max-w-7xl mx-auto flex space-x-1 sm:space-x-4 overflow-x-auto py-2">
            <button
              onClick={() => setActiveTab('knowledge')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-semibold transition-all ${
                activeTab === 'knowledge' ? 'bg-vit-gold text-slate-900 shadow' : 'text-slate-200 hover:bg-vit-maroon'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>1. KNOWLEDGE (AI Chat & Policies)</span>
            </button>
            <button
              onClick={() => setActiveTab('talent')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-semibold transition-all ${
                activeTab === 'talent' ? 'bg-vit-gold text-slate-900 shadow' : 'text-slate-200 hover:bg-vit-maroon'
              }`}
            >
              <Users className="w-4 h-4" />
              <span>2. TALENT (Student Search & Match)</span>
            </button>
            <button
              onClick={() => setActiveTab('research')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-semibold transition-all ${
                activeTab === 'research' ? 'bg-vit-gold text-slate-900 shadow' : 'text-slate-200 hover:bg-vit-maroon'
              }`}
            >
              <Award className="w-4 h-4" />
              <span>3. RESEARCH (Papers & Patents)</span>
            </button>
            <button
              onClick={() => { setActiveTab('profile'); if (!student360Data) loadStudentProfile(targetPrn); }}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-semibold transition-all ${
                activeTab === 'profile' ? 'bg-vit-gold text-slate-900 shadow' : 'text-slate-200 hover:bg-vit-maroon'
              }`}
            >
              <User className="w-4 h-4" />
              <span>Student 360 & Portfolio</span>
            </button>
            <button
              onClick={() => { setActiveTab('tickets'); fetchTickets(); }}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-semibold transition-all ${
                activeTab === 'tickets' ? 'bg-vit-gold text-slate-900 shadow' : 'text-slate-200 hover:bg-vit-maroon'
              }`}
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Grievance Desk</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex-1 w-full">

        {/* ================= PILLAR 1: KNOWLEDGE ================= */}
        {activeTab === 'knowledge' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Chatbot Interface */}
            <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col h-[650px]">
              <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
                  <h2 className="font-bold text-slate-800">Knowledge Copilot (RAG over {knowledgeData?.total_policy_docs || 33} Official Documents)</h2>
                </div>
                <div className="text-xs text-slate-500 flex items-center gap-1">
                  <span>Student PRN:</span>
                  <input 
                    type="text" 
                    value={chatStudentId} 
                    onChange={e => setChatStudentId(e.target.value)} 
                    className="border border-slate-300 rounded px-2 py-0.5 w-24 text-xs font-mono"
                  />
                </div>
              </div>

              {/* Chat Message History */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
                {chatMessages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[85%] rounded-lg p-3.5 shadow-sm text-sm ${
                      msg.role === 'user' 
                        ? 'bg-vit-maroon text-white rounded-br-none' 
                        : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none prose prose-sm'
                    }`}>
                      <div dangerouslySetInnerHTML={{ __html: marked.parse(msg.text) }} />
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white border border-slate-200 rounded-lg p-3 text-sm text-slate-500 flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full bg-vit-maroon animate-bounce"></div>
                      <div className="w-2 h-2 rounded-full bg-vit-maroon animate-bounce [animation-delay:0.2s]"></div>
                      <div className="w-2 h-2 rounded-full bg-vit-maroon animate-bounce [animation-delay:0.4s]"></div>
                      <span>Consulting official VIT regulations...</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Quick suggestions */}
              <div className="px-4 py-2 bg-slate-100 border-t border-slate-200 flex flex-wrap gap-1.5 text-xs">
                <span className="text-slate-500 py-1">Quick:</span>
                <button 
                  onClick={() => setChatInput("What is the CGPA to percentage conversion formula?")}
                  className="bg-white hover:bg-slate-200 text-slate-700 px-2 py-1 rounded border border-slate-300"
                >
                  CGPA Formula
                </button>
                <button 
                  onClick={() => setChatInput("What are the rules and credit limits for summer term registration?")}
                  className="bg-white hover:bg-slate-200 text-slate-700 px-2 py-1 rounded border border-slate-300"
                >
                  Summer Term Rules
                </button>
                <button 
                  onClick={() => setChatInput("Instructions for online MCQ examinations?")}
                  className="bg-white hover:bg-slate-200 text-slate-700 px-2 py-1 rounded border border-slate-300"
                >
                  MCQ Exam Instructions
                </button>
                <button 
                  onClick={() => setChatInput("MahaDBT scholarship application guidelines")}
                  className="bg-white hover:bg-slate-200 text-slate-700 px-2 py-1 rounded border border-slate-300"
                >
                  MahaDBT Scholarship
                </button>
              </div>

              {/* Chat Input */}
              <div className="p-3 border-t border-slate-200 bg-white flex gap-2">
                <input
                  type="text"
                  placeholder="Ask policy rules, syllabus, exam guidelines..."
                  value={chatInput}
                  onChange={e => setChatInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
                  className="flex-1 border border-slate-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-vit-maroon"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={chatLoading}
                  className="bg-vit-maroon hover:bg-vit-maroonDark text-white px-5 py-2 rounded-lg font-medium text-sm flex items-center gap-1 transition"
                >
                  <Send className="w-4 h-4" />
                  <span>Ask</span>
                </button>
              </div>
            </div>

            {/* Knowledge Overview & Official Documents */}
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
                <h3 className="font-bold text-slate-800 text-base mb-3 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-vit-maroon" />
                  <span>Official Policy & Academic Repository ({knowledgeData?.total_policy_docs || 33} Documents)</span>
                </h3>
                <p className="text-xs text-slate-500 mb-3">Retrieved directly from vit.edu and indexed into local vector store.</p>
                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {knowledgeData?.policy_documents?.map((doc, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs p-2 rounded bg-slate-50 border border-slate-200">
                      <span className="font-medium text-slate-700 truncate max-w-[200px]" title={doc.filename}>{doc.filename}</span>
                      <span className="text-slate-400 font-mono text-[10px]">{doc.size_kb} KB</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
                <h3 className="font-bold text-slate-800 text-base mb-3 flex items-center gap-2">
                  <Briefcase className="w-5 h-5 text-vit-goldDark" />
                  <span>Placement & Internship Highlights</span>
                </h3>
                <div className="space-y-2 text-xs">
                  {knowledgeData?.placement_highlights?.map((p, idx) => (
                    <div key={idx} className="p-2.5 rounded bg-amber-50/60 border border-amber-200 flex justify-between items-center">
                      <div>
                        <div className="font-bold text-slate-800">{p.company}</div>
                        <div className="text-slate-600">{p.role}</div>
                      </div>
                      <div className="text-right">
                        <span className="inline-block bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded text-[11px]">{p.stipend}</span>
                        <div className="text-[10px] text-slate-500">{p.location}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ================= PILLAR 2: TALENT ================= */}
        {activeTab === 'talent' && (
          <div className="space-y-6">
            {/* Top Filter Bar */}
            <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                <div>
                  <h2 className="text-lg font-bold text-slate-800">Student Talent Repository (1,000 Verified Students)</h2>
                  <p className="text-xs text-slate-500">Query deterministic academic records, project experience, hackathon awards, and skills.</p>
                </div>
                <div className="text-xs font-semibold text-slate-600 bg-slate-100 px-3 py-1.5 rounded-full border border-slate-300">
                  Showing {talentStudents.length} of {talentTotal} matching candidates
                </div>
              </div>

              {/* Filters Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 text-xs">
                <div>
                  <label className="block text-slate-600 font-medium mb-1">Search Keywords</label>
                  <input
                    type="text"
                    placeholder="Name, PRN, Tech..."
                    value={filters.q}
                    onChange={e => setFilters({ ...filters, q: e.target.value })}
                    className="w-full border border-slate-300 rounded p-1.5 focus:ring-1 focus:ring-vit-maroon"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 font-medium mb-1">Department / Branch</label>
                  <select
                    value={filters.branch}
                    onChange={e => setFilters({ ...filters, branch: e.target.value })}
                    className="w-full border border-slate-300 rounded p-1.5"
                  >
                    <option value="">All Branches</option>
                    <option value="CS">Computer Engg</option>
                    <option value="IT">Info Tech</option>
                    <option value="AIDS">AI & Data Science</option>
                    <option value="E&TC">Electronics & Telecomm</option>
                    <option value="MECH">Mechanical Engg</option>
                    <option value="CHEM">Chemical Engg</option>
                    <option value="INSTRU">Instrumentation</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-600 font-medium mb-1">Academic Year</label>
                  <select
                    value={filters.year}
                    onChange={e => setFilters({ ...filters, year: e.target.value })}
                    className="w-full border border-slate-300 rounded p-1.5"
                  >
                    <option value="">All Years</option>
                    <option value="FY">First Year (FY)</option>
                    <option value="SY">Second Year (SY)</option>
                    <option value="TY">Third Year (TY)</option>
                    <option value="BTECH">Final Year B.Tech</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-600 font-medium mb-1">Min CGPA</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="10"
                    placeholder="e.g. 8.5"
                    value={filters.min_cgpa}
                    onChange={e => setFilters({ ...filters, min_cgpa: e.target.value })}
                    className="w-full border border-slate-300 rounded p-1.5"
                  />
                </div>
                <div className="flex flex-col justify-end">
                  <label className="flex items-center space-x-2 text-slate-700 cursor-pointer pb-2">
                    <input
                      type="checkbox"
                      checked={filters.has_hackathon}
                      onChange={e => setFilters({ ...filters, has_hackathon: e.target.checked })}
                      className="rounded text-vit-maroon"
                    />
                    <span>Has Hackathon Win</span>
                  </label>
                </div>
                <div className="flex flex-col justify-end">
                  <label className="flex items-center space-x-2 text-slate-700 cursor-pointer pb-2">
                    <input
                      type="checkbox"
                      checked={filters.has_internship}
                      onChange={e => setFilters({ ...filters, has_internship: e.target.checked })}
                      className="rounded text-vit-maroon"
                    />
                    <span>Has Internship</span>
                  </label>
                </div>
              </div>
            </div>

            {/* AI Smart Role Matcher (Faculty Requirement Tool) */}
            <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-5 h-5 text-amber-600" />
                <h3 className="font-bold text-slate-900 text-sm">Smart Role Matcher (Faculty Recruiter AI)</h3>
              </div>
              <p className="text-xs text-slate-600 mb-3">
                Describe your project or lab requirements. AI will rank best-fit candidates — <span className="font-semibold text-amber-700">respecting all active filters above</span> (branch, year, CGPA, etc.).
              </p>

              {/* Active filter badges */}
              {(filters.branch || filters.year || filters.min_cgpa || filters.domain || filters.has_hackathon || filters.has_internship) && (
                <div className="flex flex-wrap gap-1.5 mb-3 p-2 bg-amber-100/60 rounded-lg border border-amber-200">
                  <span className="text-[11px] text-amber-700 font-semibold self-center">Filters active:</span>
                  {filters.branch && <span className="bg-amber-200 text-amber-900 text-[11px] px-2 py-0.5 rounded-full font-medium">Dept: {filters.branch}</span>}
                  {filters.year && <span className="bg-amber-200 text-amber-900 text-[11px] px-2 py-0.5 rounded-full font-medium">Year: {filters.year}</span>}
                  {filters.min_cgpa && <span className="bg-amber-200 text-amber-900 text-[11px] px-2 py-0.5 rounded-full font-medium">Min CGPA: {filters.min_cgpa}</span>}
                  {filters.domain && <span className="bg-amber-200 text-amber-900 text-[11px] px-2 py-0.5 rounded-full font-medium">Domain: {filters.domain}</span>}
                  {filters.has_hackathon && <span className="bg-amber-200 text-amber-900 text-[11px] px-2 py-0.5 rounded-full font-medium">Has Hackathon Win</span>}
                  {filters.has_internship && <span className="bg-amber-200 text-amber-900 text-[11px] px-2 py-0.5 rounded-full font-medium">Has Internship</span>}
                </div>
              )}

              <div className="flex gap-2">
                <textarea
                  rows="2"
                  placeholder="e.g. Need 3rd or 4th year students with AWS Cloud experience, Python, and Hackathon finalist status"
                  value={roleRequirement}
                  onChange={e => setRoleRequirement(e.target.value)}
                  className="flex-1 border border-amber-300 rounded-lg p-2.5 text-xs bg-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
                <button
                  onClick={handleRecommendRole}
                  disabled={recommendLoading}
                  className="bg-amber-600 hover:bg-amber-700 text-white font-semibold px-5 rounded-lg text-xs flex items-center justify-center transition"
                >
                  {recommendLoading ? 'Matching...' : 'Match Candidates'}
                </button>
              </div>

              {/* Recommendations Result View */}
              {recommendations && (
                <div className="mt-4 space-y-3 pt-3 border-t border-amber-200">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Top AI Recommendations:</h4>
                    <span className="text-[11px] text-slate-500">{recommendations.length} candidate{recommendations.length !== 1 ? 's' : ''} matched</span>
                  </div>
                  {recommendations.length === 0 ? (
                    <div className="text-xs text-slate-500 py-4 text-center bg-white rounded-lg border border-amber-200">
                      No candidates matched the current filters and requirement. Try relaxing some filters (e.g. lower min CGPA or remove branch filter).
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {recommendations.map((rec, i) => (
                        <div key={i} className="bg-white p-3 rounded-lg border border-amber-300 shadow-sm text-xs">
                          <div className="flex justify-between items-start mb-1">
                            <span className="font-bold text-slate-900 text-sm">{rec.student_name}</span>
                            <span className="bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded text-[11px]">Match: {rec.score}/100</span>
                          </div>
                          <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-slate-600 mb-1.5">
                            <span>{rec.branch}</span>
                            <span>•</span>
                            <span>{rec.year}</span>
                            {rec.cgpa != null && (
                              <span className="font-bold text-emerald-700">• CGPA: {typeof rec.cgpa === 'number' ? rec.cgpa.toFixed(2) : rec.cgpa}</span>
                            )}
                          </div>
                          <div className="text-[10px] text-slate-400 font-mono mb-1.5">PRN: {rec.prn_or_roll_no}</div>
                          <p className="text-slate-700 bg-slate-50 p-2 rounded border border-slate-200 mb-2 italic">"{rec.recommendation_reason}"</p>
                          <button
                            onClick={() => loadStudentProfile(rec.prn_or_roll_no)}
                            className="text-vit-maroon font-semibold flex items-center hover:underline text-[11px]"
                          >
                            <span>Open Full 360 Profile</span>
                            <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>


            {/* Student Directory Cards */}
            {talentLoading ? (
              <div className="text-center py-12 text-slate-500 text-sm">Loading student records...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {talentStudents.map((s, idx) => (
                  <div key={idx} className="bg-white rounded-xl p-4 shadow-sm border border-slate-200 hover:border-vit-maroon/50 transition">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-bold text-slate-900 text-base">{s.student_name}</h4>
                        <p className="text-xs font-mono text-slate-500">PRN: {s.PRN_or_Roll_No}</p>
                      </div>
                      <span className="bg-emerald-100 text-emerald-800 font-bold text-xs px-2 py-1 rounded">
                        CGPA: {s.cgpa}
                      </span>
                    </div>

                    <div className="text-xs text-slate-600 mb-2">
                      <span className="font-medium text-slate-800">{s.branch}</span> ({s.year})
                    </div>

                    <div className="bg-slate-50 p-2 rounded border border-slate-200 mb-3 text-xs">
                      <span className="text-slate-500 block text-[10px] uppercase font-semibold">Primary Domain</span>
                      <span className="font-semibold text-slate-800">{s.primary_domain}</span>
                      <div className="text-[11px] text-slate-500 truncate mt-1">Tech: {s.technologies}</div>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                      <span className="text-slate-400">{s.email}</span>
                      <button
                        onClick={() => loadStudentProfile(s.PRN_or_Roll_No)}
                        className="text-vit-maroon font-semibold flex items-center hover:underline"
                      >
                        <span>Profile 360</span>
                        <ChevronRight className="w-4 h-4 ml-0.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ================= PILLAR 3: RESEARCH ================= */}
        {activeTab === 'research' && (
          <div className="space-y-6">
            <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                <div>
                  <h2 className="text-lg font-bold text-slate-800">Research & Intellectual Property (IP) Explorer</h2>
                  <p className="text-xs text-slate-500">Discover IEEE/Springer conference papers, journal publications, and Indian patents/software copyrights.</p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={() => { setResearchType('all'); }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${researchType === 'all' ? 'bg-vit-maroon text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
                  >
                    All ({researchTotal})
                  </button>
                  <button
                    onClick={() => { setResearchType('papers'); }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${researchType === 'papers' ? 'bg-vit-maroon text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
                  >
                    Research Papers ({researchPapersTotal})
                  </button>
                  <button
                    onClick={() => { setResearchType('patents'); }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${researchType === 'patents' ? 'bg-vit-maroon text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
                  >
                    Patents & Copyrights ({researchPatentsTotal})
                  </button>
                </div>
              </div>

              {/* Research Search & Domain Filter */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
                <div className="md:col-span-2 relative">
                  <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search by paper title, patent title, authors, venue, or DOI/Application No..."
                    value={researchQuery}
                    onChange={e => setResearchQuery(e.target.value)}
                    className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-xs focus:ring-1 focus:ring-vit-maroon focus:outline-none"
                  />
                </div>
                <div>
                  <select
                    value={researchDomain}
                    onChange={e => setResearchDomain(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg p-2 text-xs bg-white focus:ring-1 focus:ring-vit-maroon focus:outline-none"
                  >
                    <option value="">All Engineering Domains ({researchAvailableDomains.length || 38})</option>
                    {researchAvailableDomains.map((d, idx) => (
                      <option key={idx} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Quick Domain Pills */}
              <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-100 text-xs">
                <span className="text-slate-500 font-medium py-0.5">Top Domains:</span>
                {[
                  "Computer Vision", "Deep Learning", "Robotics & Automation", 
                  "Electric Vehicles (EV)", "IoT & Sensor Networks", "Cybersecurity", 
                  "Green Energy & Biofuels", "Biomedical Instrumentation"
                ].map((d, idx) => (
                  <button
                    key={idx}
                    onClick={() => setResearchDomain(researchDomain === d ? '' : d)}
                    className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition ${
                      researchDomain === d 
                        ? 'bg-amber-100 text-amber-900 border border-amber-300 font-bold' 
                        : 'bg-slate-50 text-slate-700 hover:bg-slate-100 border border-slate-200'
                    }`}
                  >
                    {d}
                  </button>
                ))}
                {researchDomain && (
                  <button
                    onClick={() => setResearchDomain('')}
                    className="text-[11px] text-red-600 hover:underline ml-1 font-semibold"
                  >
                    Clear Filter
                  </button>
                )}
              </div>
            </div>

            {/* Research Results Grid */}
            {researchLoading ? (
              <div className="text-center py-12 text-slate-500 text-sm">Searching research database...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {researchItems.map((item, idx) => (
                  <div key={idx} className="bg-white rounded-xl p-5 shadow-sm border border-slate-200 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <span className={`text-[11px] font-bold px-2 py-0.5 rounded uppercase ${
                          item.type === 'Research Paper' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-amber-100 text-amber-900 border border-amber-300'
                        }`}>
                          {item.type}
                        </span>
                        <span className="text-xs text-slate-400 font-mono">{item.year}</span>
                      </div>

                      <h4 className="font-bold text-slate-900 text-sm mb-2 leading-snug">{item.title}</h4>
                      <p className="text-xs text-slate-600 mb-1"><span className="font-semibold text-slate-700">Venue / Status:</span> {item.venue_or_status}</p>
                      <p className="text-xs text-slate-600 mb-2"><span className="font-semibold text-slate-700">Domain:</span> {item.domain}</p>
                      
                      <div className="bg-slate-50 p-2.5 rounded border border-slate-200 text-xs">
                        <div className="font-medium text-slate-800">Authors: {item.authors}</div>
                        {item.email && <div className="text-slate-500 text-[11px]">Contact: {item.email}</div>}
                        {item.url_or_no && (
                          <div className="text-vit-maroon font-mono text-[11px] truncate mt-1">
                            Ref: {item.url_or_no}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-xs">
                      <span className="text-slate-500">Student: {item.student_name}</span>
                      <button
                        onClick={() => loadStudentProfile(item.prn)}
                        className="text-vit-maroon font-semibold hover:underline flex items-center"
                      >
                        <span>View Author 360</span>
                        <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ================= STUDENT 360 & PORTFOLIO ================= */}
        {activeTab === 'profile' && (
          <div className="space-y-6">
            <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-slate-800">Student 360 Profile & Resume Generator</h2>
                <p className="text-xs text-slate-500">Unified profile aggregating academic projects, internships, hackathons, certifications, and research publications.</p>
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter PRN (e.g. 12110452)"
                  value={targetPrn}
                  onChange={e => setTargetPrn(e.target.value)}
                  className="border border-slate-300 rounded px-3 py-1.5 text-xs font-mono"
                />
                <button
                  onClick={() => loadStudentProfile(targetPrn)}
                  className="bg-vit-maroon hover:bg-vit-maroonDark text-white px-4 py-1.5 rounded text-xs font-semibold transition"
                >
                  Load Profile
                </button>
              </div>
            </div>

            {profileLoading ? (
              <div className="text-center py-16 text-slate-500">Loading student 360 data...</div>
            ) : student360Data && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Profile Card */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 space-y-4">
                  <div className="text-center pb-4 border-b border-slate-100">
                    <div className="w-20 h-20 rounded-full bg-slate-100 border-2 border-vit-maroon mx-auto flex items-center justify-center text-vit-maroon font-bold text-2xl mb-2">
                      {student360Data.student_name ? student360Data.student_name[0] : 'S'}
                    </div>
                    <h3 className="font-bold text-slate-900 text-lg">{student360Data.student_name}</h3>
                    <p className="text-xs text-slate-500 font-mono">PRN: {student360Data.prn_or_roll_no}</p>
                    <span className="inline-block mt-2 bg-vit-maroon text-white font-semibold text-xs px-3 py-1 rounded-full">
                      Track: {student360Data.suggested_career_track}
                    </span>
                  </div>

                  <div className="text-xs space-y-2 text-slate-700">
                    <div className="flex justify-between py-1 border-b border-slate-50">
                      <span className="text-slate-500">Branch:</span>
                      <span className="font-medium">{student360Data.branch}</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-50">
                      <span className="text-slate-500">Year of Study:</span>
                      <span className="font-medium">{student360Data.year}</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-50">
                      <span className="text-slate-500">CGPA:</span>
                      <span className="font-bold text-emerald-700">
                        {student360Data.cgpa != null ? student360Data.cgpa.toFixed ? student360Data.cgpa.toFixed(2) : student360Data.cgpa : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-50">
                      <span className="text-slate-500">Total Records:</span>
                      <span className="font-semibold text-emerald-700">{student360Data.total_records} verified</span>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold text-slate-800 uppercase mb-2">Strongest Domains</h4>
                    <div className="flex flex-wrap gap-1.5">
                      {student360Data.strongest_domains?.map((d, i) => (
                        <span key={i} className="bg-slate-100 text-slate-800 text-[11px] px-2 py-0.5 rounded border border-slate-200">
                          {d}
                        </span>
                      ))}
                    </div>
                  </div>

                  {student360Data.top_companies && student360Data.top_companies.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold text-slate-800 uppercase mb-2">Industry Associations</h4>
                      <div className="flex flex-wrap gap-1.5">
                        {student360Data.top_companies.map((c, i) => (
                          <span key={i} className="bg-amber-50 text-amber-900 border border-amber-200 text-[11px] px-2 py-0.5 rounded font-medium">
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Portfolio / Verified Activity Records */}
                <div className="lg:col-span-2 space-y-6">
                  {portfolioData && (
                    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
                      <div className="flex justify-between items-center mb-3">
                        <h3 className="font-bold text-slate-900 text-base">{portfolioData.headline}</h3>
                        <span className="text-xs bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full font-semibold">Verified Portfolio</span>
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-lg border border-slate-200 mb-4">
                        {portfolioData.summary}
                      </p>

                      <div className="space-y-4">
                        {Object.entries(portfolioData.sections || {}).map(([key, section], idx) => {
                          if (!section.records || section.records.length === 0) return null;
                          return (
                            <div key={idx} className="border-t border-slate-100 pt-3">
                              <h4 className="font-bold text-slate-800 text-xs uppercase mb-2 flex items-center justify-between">
                                <span>{section.label}</span>
                                <span className="text-slate-400 font-normal">({section.count})</span>
                              </h4>
                              <div className="space-y-1.5">
                                {section.records.map((r, rIdx) => (
                                  <div key={rIdx} className="text-xs p-2.5 rounded bg-slate-50 border border-slate-200">
                                    <div className="font-semibold text-slate-800">
                                      {r.Project_Title || r.Certification_Title || r.Hackathon_Name || r.Paper_Title || r.Title || r.Internship_Role}
                                    </div>
                                    <div className="text-[11px] text-slate-600 mt-0.5">
                                      {r.Company_Name || r.Internship_Company_Name || r.Platform_or_Provider || r.Venue_Name || r.Result_Status || r.IP_Type}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ================= GRIEVANCE DESK ================= */}
        {activeTab === 'tickets' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
              <h2 className="text-base font-bold text-slate-900 mb-1">Lodge a Student Complaint / Grievance</h2>
              <p className="text-xs text-slate-500 mb-4">Your ticket will be recorded in the college database and assigned a tracking ID.</p>

              {ticketSuccess && (
                <div className="mb-4 p-3 bg-emerald-50 border border-emerald-300 text-emerald-800 rounded-lg text-xs flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  <span>{ticketSuccess}</span>
                </div>
              )}

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-700 font-medium mb-1">Student PRN / Roll No</label>
                  <input
                    type="text"
                    value={ticketStudentId}
                    onChange={e => setTicketStudentId(e.target.value)}
                    className="w-full border border-slate-300 rounded p-2 focus:ring-1 focus:ring-vit-maroon font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-medium mb-1">Describe Your Issue</label>
                  <textarea
                    rows="4"
                    placeholder="e.g. My grade sheet has an incorrect score for Semester 5 exam or issue with lab equipment booking..."
                    value={ticketDescription}
                    onChange={e => setTicketDescription(e.target.value)}
                    className="w-full border border-slate-300 rounded p-2 focus:ring-1 focus:ring-vit-maroon"
                  />
                </div>
                <button
                  onClick={handleCreateTicket}
                  className="bg-vit-maroon hover:bg-vit-maroonDark text-white px-5 py-2 rounded-lg font-semibold text-xs transition"
                >
                  Submit Complaint Ticket
                </button>
              </div>
            </div>

            <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-slate-900 text-base">Your Registered Tickets</h3>
                <button 
                  onClick={fetchTickets}
                  className="text-xs text-vit-maroon font-semibold hover:underline"
                >
                  Refresh
                </button>
              </div>

              {ticketsList.length === 0 ? (
                <p className="text-xs text-slate-500 py-6 text-center">No active tickets found for student {ticketStudentId}.</p>
              ) : (
                <div className="space-y-2.5">
                  {ticketsList.map((t, idx) => (
                    <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs">
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-bold text-slate-900">Ticket #{t.ticket_id}</span>
                        <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded text-[10px] font-semibold uppercase">{t.status}</span>
                      </div>
                      <p className="text-slate-700 mb-1.5">{t.description}</p>
                      <div className="text-[10px] text-slate-400">Created: {t.created_at}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

      </main>

      {/* Institutional Footer */}
      <footer className="bg-slate-900 text-slate-400 text-xs py-5 border-t border-slate-800 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center gap-3">
          <p>© 2026 Vishwakarma Institute of Technology (VIT), Pune. All Rights Reserved.</p>
          <div className="flex space-x-4">
            <span className="text-slate-500">Autonomous Institute</span>
            <span className="text-slate-500">666, Upper Indiranagar, Bibwewadi, Pune - 411037</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
