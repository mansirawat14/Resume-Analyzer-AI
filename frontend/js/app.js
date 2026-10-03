/**
 * RESUMATE AI - Frontend Application Core Logic
 * Handles:
 * - Dual Light/Dark Theme Switch & Synchronization (Login & Dashboard)
 * - Session & Authentication handling (Sign In, Sign Up, Quick Demo)
 * - View Navigation & Tab Routing across all 10 Screens
 * - Interactive File Upload Simulation & Progress
 * - Live Animated Analyzing Screen with Checklist progression
 * - Interactive AI Suggestions & Real-Time Score Updates
 * - Job Match Analyzer with dynamic role switching
 * - Report Exporter & Toast Notifications
 */

// Application State
let selectedResumeFile = null;
let resumeAnalysisData = null;
const appState = {
  theme: localStorage.getItem('resumate_theme') || 'light',
  isAuthenticated: false,
  currentUser: {
    name: 'Rahul Sharma',
    email: 'rahul@example.com',
    role: 'Senior Developer'
  },
  currentView: 'landing', // 'landing', 'upload', 'analyzing', 'dashboard', 'skills', 'jobmatch', 'suggestions', 'sections', 'history', 'mobile'
  resumeScore: 82,
  issuesCount: 8,
  appliedSuggestions: new Set()
};

// =========================================================================
// THEME SWITCH & PERSISTENCE
// =========================================================================

/**
 * Initializes and synchronizes theme across the entire application
 */
function initializeTheme() {
  const savedTheme = localStorage.getItem('resumate_theme') || 'light';
  applyTheme(savedTheme);
}

/**
 * Toggles theme based on checkbox state
 * @param {boolean} isDark 
 */
function toggleAppTheme(isDark) {
  const newTheme = isDark ? 'dark' : 'light';
  applyTheme(newTheme);
}

/**
 * Applies theme to DOM and syncs both toggle switches (Login & Dashboard)
 * @param {'light'|'dark'} theme 
 */
function applyTheme(theme) {
  appState.theme = theme;
  localStorage.setItem('resumate_theme', theme);

  const authToggle = document.getElementById('authThemeToggle');
  const dashToggle = document.getElementById('dashThemeToggle');
  const authThemeLabel = document.getElementById('authThemeLabel');

  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
    if (authToggle) authToggle.checked = true;
    if (dashToggle) dashToggle.checked = true;
    if (authThemeLabel) authThemeLabel.textContent = 'Dark Mode';
  } else {
    document.documentElement.classList.remove('dark');
    if (authToggle) authToggle.checked = false;
    if (dashToggle) dashToggle.checked = false;
    if (authThemeLabel) authThemeLabel.textContent = 'Light Mode';
  }
}

// =========================================================================
// AUTHENTICATION & LOGIN FLOW
// =========================================================================

 let authMode = 'signin';
/**
 * Switch between Sign In and Sign Up tabs on the Login Card
 * @param {'signin'|'signup'} tab 
 */
function switchAuthTab(tab) {
  authMode = tab;
  const tabSignIn = document.getElementById('tabSignIn');
  const tabSignUp = document.getElementById('tabSignUp');
  const nameFieldGroup = document.getElementById('nameFieldGroup');
  const authSubmitBtn = document.getElementById('authSubmitBtn');

  if (tab === 'signup') {
    tabSignUp.className = 'flex-1 pb-2.5 text-xs sm:text-sm font-bold border-b-2 border-indigo-500 text-indigo-500 transition-all';
    tabSignIn.className = 'flex-1 pb-2.5 text-xs sm:text-sm font-semibold border-b-2 border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all';
    if (nameFieldGroup) nameFieldGroup.classList.remove('hidden');
    if (authSubmitBtn) authSubmitBtn.textContent = 'Create RESUMATE Account';
  } else {
    tabSignIn.className = 'flex-1 pb-2.5 text-xs sm:text-sm font-bold border-b-2 border-indigo-500 text-indigo-500 transition-all';
    tabSignUp.className = 'flex-1 pb-2.5 text-xs sm:text-sm font-semibold border-b-2 border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all';
    if (nameFieldGroup) nameFieldGroup.classList.add('hidden');
    if (authSubmitBtn) authSubmitBtn.textContent = 'Log In';
  }
}

/**
 * Handle form submission
 * @param {Event} e 
 */
async function handleAuthSubmit(e) {
  e.preventDefault();

  const emailInput = document.getElementById('authEmail');
  const passwordInput = document.getElementById('authPassword');
  const nameInput = document.getElementById('authName');

  const email = emailInput ? emailInput.value.trim() : '';
  const password = passwordInput ? passwordInput.value : '';
  const name = nameInput ? nameInput.value.trim() : '';

  if (!email || !password) {
    showToast('Please enter your email and password.', true);
    return;
  }

  if (authMode === 'signup' && !name) {
    showToast('Please enter your full name.', true);
    return;
  }

  try {
    const endpoint =
      authMode === 'signup'
        ? 'http://127.0.0.1:5000/api/auth/register'
        : 'http://127.0.0.1:5000/api/auth/login';

    const requestBody =
      authMode === 'signup'
        ? {
            name: name,
            email: email,
            password: password
          }
        : {
            email: email,
            password: password
          };

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.message || 'Authentication failed.');
    }

    // Save JWT token
    localStorage.setItem('resumate_token', data.access_token);

    const userName = data.user?.name || name || 'User';
    const userEmail = data.user?.email || email;

    if (authMode === 'signup') {
      showToast('Account created successfully!');

      // Switch back to Sign In after registration
      switchAuthTab('signin');

      // Keep the email ready for login
      if (emailInput) {
        emailInput.value = userEmail;
      }

      // Clear password
      if (passwordInput) {
        passwordInput.value = '';
      }

      return;
    }

    // Login successful
    loginSuccess(userName, userEmail);

  } catch (error) {
    console.error('Authentication error:', error);
    showToast(error.message || 'Unable to connect to the server.', true);
  }
}
/**
 * One-Click Quick Demo Login for instant testing
 */
function quickDemoLogin() {
  showToast('Please use your email and password to log in.', true);
}

function resetDashboardForNewUser() {
  const healthCard = document.getElementById('resumeHealthCard');
  const scoreCard = document.getElementById('scoreOverviewCard');
  const strengthsCard = document.getElementById('topStrengthsCard');

  if (healthCard) {
    healthCard.innerHTML = `
      <div>
        <h3 class="text-sm font-bold text-[var(--text-primary)]">
          Resume Health
        </h3>
        <p class="text-xs text-[var(--text-muted)] mt-0.5">
          Overall benchmark against industry
        </p>
      </div>

      <div class="my-6 flex flex-col items-center">
        <div class="w-32 h-32 relative flex items-center justify-center">
          <div class="text-4xl font-extrabold text-[var(--text-muted)]">
            —
          </div>
        </div>

        <div class="text-center mt-3">
          <div class="text-sm font-bold text-[var(--text-secondary)]">
            No analysis yet
          </div>
          <p class="text-xs text-[var(--text-secondary)] mt-1 max-w-[220px]">
            Upload your resume to see your resume health.
          </p>
        </div>
      </div>

      <button
        onclick="navigateTo('upload')"
        class="w-full py-2 rounded-xl bg-[var(--bg-card-subtle)] border border-[var(--border-subtle)] text-xs font-semibold hover:bg-[var(--bg-card-hover)] transition-colors"
      >
        Upload Resume
      </button>
    `;
  }

  if (scoreCard) {
    scoreCard.innerHTML = `
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-sm font-bold text-[var(--text-primary)]">
            Score Overview
          </h3>
          <p class="text-xs text-[var(--text-muted)] mt-0.5">
            Resume version improvement over time
          </p>
        </div>
      </div>

      <div class="flex-1 flex items-center justify-center min-h-[220px]">
        <div class="text-center">
          <div class="text-4xl font-extrabold text-[var(--text-muted)]">
            —
          </div>
          <p class="text-sm text-[var(--text-secondary)] mt-2">
            No resume analysis yet
          </p>
          <p class="text-xs text-[var(--text-muted)] mt-1">
            Upload and analyze your resume to see your score history.
          </p>
        </div>
      </div>
    `;
  }

  if (strengthsCard) {
    strengthsCard.innerHTML = `
      <div>
        <h3 class="text-sm font-bold text-[var(--text-primary)]">
          Top Strengths
        </h3>
        <p class="text-xs text-[var(--text-muted)] mt-0.5">
          High-impact positive factors
        </p>
      </div>

      <div class="flex-1 flex items-center justify-center text-center">
        <div>
          <div class="text-3xl mb-2">📄</div>
          <p class="text-sm font-semibold text-[var(--text-secondary)]">
            No strengths yet
          </p>
          <p class="text-xs text-[var(--text-muted)] mt-1">
            Analyze your resume to discover your strengths.
          </p>
        </div>
      </div>

      <button
        onclick="navigateTo('upload')"
        class="w-full py-2 rounded-xl bg-[var(--bg-card-subtle)] border border-[var(--border-subtle)] text-xs font-semibold hover:bg-[var(--bg-card-hover)] transition-colors"
      >
        Analyze Resume
      </button>
    `;
  }
}

function toggleNotifications() {
    let panel = document.getElementById("notificationPanel");

    if (!panel) {
        panel = document.createElement("div");

        panel.id = "notificationPanel";

        panel.className =
            "fixed top-16 right-6 w-80 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl shadow-2xl z-50 overflow-hidden";

        panel.innerHTML = `
            <div class="px-4 py-3 border-b border-[var(--border-color)] flex items-center justify-between">
                <h3 class="text-sm font-bold text-[var(--text-primary)]">
                    Notifications
                </h3>
                <span class="text-xs text-[var(--text-muted)]">
                    0 new
                </span>
            </div>

            <div class="px-4 py-8 text-center">
                <div class="text-2xl mb-2">🔔</div>
                <p class="text-sm font-semibold text-[var(--text-primary)]">
                    No notifications
                </p>
                <p class="text-xs text-[var(--text-muted)] mt-1">
                    You're all caught up!
                </p>
            </div>
        `;

        document.body.appendChild(panel);
    } else {
        panel.remove();
    }
}

/**
 * Complete login process and transition to Dashboard with current theme intact
 */
function loginSuccess(name, email) {
  appState.isAuthenticated = true;

  resetDashboardForNewUser();
  
  appState.currentUser.name = name;
  appState.currentUser.email = email;

  const authView = document.getElementById('authView');
  const dashboardView = document.getElementById('dashboardView');
  const userNameDisplay = document.getElementById('userNameDisplay');
  const dashboardGreeting = document.getElementById('dashboardGreeting');

  if (userNameDisplay) userNameDisplay.textContent = name;

  if (dashboardGreeting) {
    dashboardGreeting.textContent = `Hello, ${name} 👋`;
  }

  // Fade out auth, fade in dashboard
  authView.classList.add('hidden');
  dashboardView.classList.remove('hidden');

  // Sync theme switch in dashboard header
  applyTheme(appState.theme);

  showToast(`Welcome back, ${name}! Your resume report is ready.`);
  navigateTo('dashboard');
}

/**
 * Log out and return to Login screen with current theme preserved
 */
function logout() {
  appState.isAuthenticated = false;
  const authView = document.getElementById('authView');
  const dashboardView = document.getElementById('dashboardView');

  dashboardView.classList.add('hidden');
  authView.classList.remove('hidden');

  // Maintain current theme switch state on login screen
  applyTheme(appState.theme);
  showToast('You have been signed out safely.');
}

/**
 * Toggle password reveal
 */
function togglePasswordVisibility() {
  const input = document.getElementById('authPassword');
  if (!input) return;
  input.type = input.type === 'password' ? 'text' : 'password';
}

// =========================================================================
// NAVIGATION & VIEW ROUTING
// =========================================================================

/**
 * Navigate to a specific sub-view
 * @param {string} viewName 
 */
function navigateTo(viewName) {
  appState.currentView = viewName;

  // Hide all sub-views
  const views = document.querySelectorAll('.app-subview');
  views.forEach(v => v.classList.add('hidden'));

  // Show requested view
  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) {
    targetView.classList.remove('hidden');
  }

  // Update sidebar active links
  const links = document.querySelectorAll('.sidebar-link');
  links.forEach(l => l.classList.remove('active'));

  const activeLink = document.getElementById(`nav-${viewName}`);
  if (activeLink) {
    activeLink.classList.add('active');
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// =========================================================================
// RESUME UPLOAD & ANALYSIS SIMULATION
// =========================================================================

function triggerFileInput() {
  const input = document.getElementById('resumeFileInput');
  if (input) input.click();
}

function handleFileSelected(event) {

  const file = event.target.files && event.target.files[0];

  if (!file) return;

  // Save selected file
  selectedResumeFile = file;

  // Get UI elements
  const fileNameDisplay =
    document.getElementById('fileNameDisplay');

  const fileSizeDisplay =
    document.getElementById('fileSizeDisplay');

  const fileTypeDisplay =
    document.getElementById('fileTypeDisplay');

  const progressBar =
    document.getElementById('fileUploadProgressBar');

  const percentDisplay =
    document.getElementById('filePercentDisplay');

  const uploadCheck =
    document.getElementById('fileUploadCheck');


  // -------------------------------
  // FILE NAME
  // -------------------------------

  if (fileNameDisplay) {
    fileNameDisplay.textContent = file.name;
  }


  // -------------------------------
  // FILE SIZE
  // -------------------------------

  if (fileSizeDisplay) {

    const sizeMB =
      file.size / (1024 * 1024);

    fileSizeDisplay.textContent =
      sizeMB < 1
        ? `${(file.size / 1024).toFixed(0)} KB`
        : `${sizeMB.toFixed(1)} MB`;
  }


  // -------------------------------
  // FILE TYPE
  // -------------------------------

  if (fileTypeDisplay) {

    const extension =
      file.name
        .split('.')
        .pop()
        .toUpperCase();

    fileTypeDisplay.textContent =
      extension;
  }


  // -------------------------------
  // PROGRESS
  // -------------------------------

  if (progressBar) {
    progressBar.style.width = '100%';
  }

  if (percentDisplay) {
    percentDisplay.textContent = '100%';

    percentDisplay.classList.remove(
      'text-[var(--text-muted)]'
    );

    percentDisplay.classList.add(
      'text-emerald-500'
    );
  }


  // -------------------------------
  // SUCCESS CHECKMARK
  // -------------------------------

  if (uploadCheck) {
    uploadCheck.classList.remove('hidden');
  }


  // -------------------------------
  // SUCCESS MESSAGE
  // -------------------------------

  showToast(
    `Resume "${file.name}" selected successfully!`
  );
}

/**
 * Start simulated AI analyzing pipeline with animated checklist
 */
async function startAnalyzingResume() {

  if (!selectedResumeFile) {
    showToast('Please select a resume first.', true);
    return;
  }

  navigateTo('analyzing');

  const circle =
    document.getElementById('analyzingProgressCircle');

  const percentNum =
    document.getElementById('analyzingPercentNum');

  const stepRead =
    document.getElementById('step-read');

  const stepSkills =
    document.getElementById('step-skills');

  const stepExp =
    document.getElementById('step-exp');

  const stepKeywords =
    document.getElementById('step-keywords');

  const stepInsights =
    document.getElementById('step-insights');

  // Start progress animation
  if (circle) {
    circle.style.strokeDashoffset = '200';
  }

  if (percentNum) {
    percentNum.textContent = '20%';
  }

  const checkSvg = `
    <svg class="w-4 h-4 text-emerald-500"
         fill="none"
         stroke="currentColor"
         viewBox="0 0 24 24">
      <path stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2.5"
            d="M5 13l4 4L19 7">
      </path>
    </svg>
  `;

  const spinnerSvg = `
    <div class="w-4 h-4 rounded-full
                border-2 border-indigo-500
                border-t-transparent animate-spin">
    </div>
  `;

  // Update animation while backend processes
  setTimeout(() => {

    if (circle) {
      circle.style.strokeDashoffset = '145';
    }

    if (percentNum) {
      percentNum.textContent = '45%';
    }

    if (stepRead) {
      stepRead.innerHTML = `
        <span class="font-medium">
          Reading resume
        </span>
        ${checkSvg}
      `;
    }

    if (stepSkills) {
      stepSkills.innerHTML = `
        <span class="font-medium">
          Extracting skills
        </span>
        ${spinnerSvg}
      `;
    }

  }, 500);


  setTimeout(() => {

    if (circle) {
      circle.style.strokeDashoffset = '63';
    }

    if (percentNum) {
      percentNum.textContent = '76%';
    }

    if (stepSkills) {
      stepSkills.innerHTML = `
        <span class="font-medium">
          Extracting skills
        </span>
        ${checkSvg}
      `;
    }

    if (stepExp) {
      stepExp.innerHTML = `
        <span class="font-medium">
          Analyzing experience
        </span>
        ${checkSvg}
      `;
    }

    if (stepKeywords) {
      stepKeywords.innerHTML = `
        <span class="font-medium">
          Checking keywords
        </span>
        ${spinnerSvg}
      `;
    }

    if (stepInsights) {
      stepInsights.classList.remove('opacity-60');

      stepInsights.innerHTML = `
        <span class="font-medium">
          Generating insights
        </span>
        ${spinnerSvg}
      `;
    }

  }, 1200);


  try {

    // Create form data
    const formData = new FormData();

    formData.append(
      'resume',
      selectedResumeFile
    );

    // Send resume to Flask backend
    const response = await fetch(
      'http://127.0.0.1:5000/api/resume/upload',
      {
        method: 'POST',
        body: formData
      }
    );

    const data = await response.json();

    // Backend error
    if (!response.ok || !data.success) {

      throw new Error(
        data.message ||
        data.error ||
        'Resume analysis failed.'
      );
    }

    // Save complete backend response
    resumeAnalysisData = data;

    // Update application state
    appState.resumeScore =
      data.resume_score ?? 0;

      // Update Resume Score circle
const resumeScoreCircle =
  document.getElementById('resumeScoreCircle');

if (resumeScoreCircle) {
  const score = Number(data.resume_score) || 0;

  resumeScoreCircle.setAttribute(
    'stroke-dasharray',
    `${score}, 100`
  );
}

    appState.issuesCount =
      data.issues_found ?? 0;


const kpiIssuesCount =
  document.getElementById('kpiIssuesCount');

if (kpiIssuesCount) {
  kpiIssuesCount.textContent =
    data.issues_found ?? 0;
}

// Update Issues Found status
const issuesStatus =
  document.getElementById('issuesStatus');

if (issuesStatus) {
  issuesStatus.textContent = 'Analysis completed';
}

      const kpiAtsScore =
  document.getElementById('kpiAtsScore');

if (kpiAtsScore) {
  kpiAtsScore.textContent =
    `${data.ats_score ?? 0}%`;
}

// Update ATS Score progress circle
const atsScoreCircle =
  document.getElementById('atsScoreCircle');

if (atsScoreCircle) {
  const score = Number(data.ats_score) || 0;

  atsScoreCircle.setAttribute(
    'stroke-dasharray',
    `${score}, 100`
  );
}
// Update ATS Score status
const atsScoreStatus =
  document.getElementById('atsScoreStatus');

if (atsScoreStatus) {
  atsScoreStatus.textContent = 'Analysis completed';
}

      // Update Resume Score on Dashboard
const kpiResumeScore =
  document.getElementById('kpiResumeScore');

if (kpiResumeScore) {
  kpiResumeScore.innerHTML =
    `${data.resume_score}<span class="text-xs text-[var(--text-muted)] font-normal">/100</span>`;
}

// Update Score Overview current score
const scoreCurrentLabel =
  document.getElementById('scoreCurrentLabel');

if (scoreCurrentLabel) {
  scoreCurrentLabel.textContent =
    data.resume_score;
}

// ============================================================
// SCORE OVERVIEW - REAL RESUME SCORE HISTORY
// ============================================================

const currentResumeScore = Number(data.resume_score) || 0;

// Get previous score history
let scoreHistory = JSON.parse(
  localStorage.getItem('resumateScoreHistory') || '[]'
);

// Add score only if it is different from the previous analysis
const lastScore = scoreHistory[scoreHistory.length - 1];

if (lastScore !== currentResumeScore) {
  scoreHistory.push(currentResumeScore);
}

// Keep only latest 4 different analyses
scoreHistory = scoreHistory.slice(-4);

// Save history
localStorage.setItem(
  'resumateScoreHistory',
  JSON.stringify(scoreHistory)
);

// ------------------------------------------------------------
// Chart elements
// ------------------------------------------------------------

const scoreChartLine =
  document.getElementById('scoreChartLine');

const scoreHistoryPoints =
  document.getElementById('scoreHistoryPoints');

  const scoreNoAnalysisText =
  document.getElementById('scoreNoAnalysisText');

if (scoreNoAnalysisText) {
  scoreNoAnalysisText.style.display =
    scoreHistory.length === 0
      ? 'block'
      : 'none';
}

const scoreChartLabels =
  document.getElementById('scoreChartLabels');

const scoreImprovement =
  document.getElementById('scoreImprovement');

// Total number of points
const totalPoints = scoreHistory.length;

// ------------------------------------------------------------
// Calculate chart coordinates
// ------------------------------------------------------------

const chartPoints = scoreHistory.map((score, index) => {

  const x =
    totalPoints === 1
      ? 270
      : 30 + (
          index * (240 / (totalPoints - 1))
        );

  const y =
    105 - (Number(score) * 0.8);

  return {
    x,
    y,
    score: Number(score)
  };
});

// ------------------------------------------------------------
// Draw line
// ------------------------------------------------------------

if (scoreChartLine && chartPoints.length > 0) {

  scoreChartLine.setAttribute(
    'points',
    chartPoints
      .map(point => `${point.x},${point.y}`)
      .join(' ')
  );
}

// ------------------------------------------------------------
// Draw points + score numbers
// ------------------------------------------------------------

if (scoreHistoryPoints) {

  scoreHistoryPoints.innerHTML = '';

  chartPoints.forEach((point, index) => {

    const isCurrent =
      index === chartPoints.length - 1;

    // Circle
    const circle =
      document.createElementNS(
        'http://www.w3.org/2000/svg',
        'circle'
      );

    circle.setAttribute('cx', point.x);
    circle.setAttribute('cy', point.y);
    circle.setAttribute(
      'r',
      isCurrent ? '5.5' : '4.5'
    );

    circle.setAttribute(
      'fill',
      isCurrent
        ? '#8b5cf6'
        : '#6366f1'
    );

    circle.setAttribute(
      'stroke',
      '#ffffff'
    );

    circle.setAttribute(
      'stroke-width',
      '2'
    );

    scoreHistoryPoints.appendChild(circle);

    // Score number
    const text =
      document.createElementNS(
        'http://www.w3.org/2000/svg',
        'text'
      );

    text.setAttribute('x', point.x);
    text.setAttribute(
      'y',
      point.y - 10
    );

    text.setAttribute(
      'text-anchor',
      'middle'
    );

    text.setAttribute(
      'font-size',
      '11'
    );

    text.setAttribute(
      'font-weight',
      'bold'
    );

    text.setAttribute(
      'fill',
      isCurrent
        ? '#8b5cf6'
        : '#ffffff'
    );

    text.textContent = point.score;

    scoreHistoryPoints.appendChild(text);
  });
}

// ------------------------------------------------------------
// Update version labels
// ------------------------------------------------------------

if (scoreChartLabels) {

  scoreChartLabels.innerHTML = '';

  scoreHistory.forEach((score, index) => {

    const label =
      document.createElement('span');

    if (index === scoreHistory.length - 1) {

      label.textContent =
        `V${index + 1} (Current)`;

      label.className =
        'text-indigo-500 font-bold';

    } else {

      label.textContent =
        `V${index + 1}`;
    }

    scoreChartLabels.appendChild(label);
  });
}

// Update Score Overview total

// Update total score
if (scoreImprovement) {
  const latestScore =
    Number(data.resume_score) || 0;

  scoreImprovement.textContent =
    `${latestScore} pts total`;
}

// Update Resume Score status
const resumeScoreStatus =
  document.getElementById('resumeScoreStatus');

if (resumeScoreStatus) {
  resumeScoreStatus.textContent = 'Analysis completed';
}

// Update Skills Match on Dashboard
// Update Skills Match on Dashboard
const kpiSkillsMatch =
    document.getElementById('kpiSkillsMatch');

// Get latest Job Match percentage
const savedJobMatch =
    localStorage.getItem('resumateJobMatchPercentage');

const dashboardMatchPercentage =
    savedJobMatch !== null
        ? Number(savedJobMatch)
        : null;

if (kpiSkillsMatch) {
    kpiSkillsMatch.textContent =
        dashboardMatchPercentage !== null
            ? `${dashboardMatchPercentage}%`
            : '0%';
}

// Update Skills Match progress circle
const skillsMatchCircle =
    document.getElementById('skillsMatchCircle');

if (skillsMatchCircle) {
    skillsMatchCircle.setAttribute(
        'stroke-dasharray',
        dashboardMatchPercentage !== null
            ? `${dashboardMatchPercentage}, 100`
            : '0, 100'
    );
}

// Update Skills Match status
const skillsMatchStatus =
    document.getElementById('skillsMatchStatus');

if (skillsMatchStatus) {
    skillsMatchStatus.textContent =
        dashboardMatchPercentage !== null
            ? 'Analysis completed'
            : 'No analysis yet';
}
const jobMatch =
    data.job_match || {};

const matchPercentage =
    jobMatch.match_percentage;

    
if (kpiSkillsMatch) {
    kpiSkillsMatch.textContent =
        matchPercentage !== null &&
        matchPercentage !== undefined
            ? `${matchPercentage}%`
            : '0%';
}


// Update Top Strengths
const topStrengthsList =
  document.getElementById('topStrengthsList');

const topStrengthsButton =
  document.getElementById('topStrengthsButton');

const topStrengths =
  data.top_strengths || [];

if (topStrengthsList) {

  topStrengthsList.innerHTML = '';

  if (topStrengths.length > 0) {

    topStrengths.forEach(item => {

      const strengthRow =
        document.createElement('div');

      strengthRow.className =
        'flex items-center gap-2.5 text-xs font-medium text-[var(--text-secondary)]';

      strengthRow.innerHTML = `
        <div class="w-5 h-5 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center shrink-0">
          <svg
            class="w-3.5 h-3.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2.5"
              d="M5 13l4 4L19 7"
            ></path>
          </svg>
        </div>

        <span>${item.strength || 'Strength identified'}</span>
      `;

      topStrengthsList.appendChild(strengthRow);
    });

    topStrengthsList.classList.remove('hidden');

    if (topStrengthsButton) {
      topStrengthsButton.classList.remove('hidden');
      topStrengthsButton.textContent =
        'View Improvement Suggestions';
    }

  } else {

    topStrengthsList.classList.add('hidden');

    if (topStrengthsButton) {
      topStrengthsButton.classList.add('hidden');
    }
  }
}

const resumeHealthStatus =
  document.getElementById('resumeHealthStatus');

if (resumeHealthStatus) {
  resumeHealthStatus.textContent =
    data.resume_health?.health ?? 'No analysis yet';
}

const resumeHealthPercent =
  document.getElementById('resumeHealthPercent');

if (resumeHealthPercent) {
  resumeHealthPercent.textContent =
    `${data.resume_health?.score ?? 0}%`;
}

const resumeHealthCircle =
  document.getElementById('resumeHealthCircle');

if (resumeHealthCircle) {
  const healthScore =
    data.resume_health?.score ?? 0;

  resumeHealthCircle.setAttribute(
    'stroke-dasharray',
    `${healthScore}, 100`
  );
}

const resumeHealthDescription =
  document.getElementById('resumeHealthDescription');

if (resumeHealthDescription) {
  const healthScore =
    data.resume_health?.score ?? 0;

  resumeHealthDescription.textContent =
    `Your resume health score is ${healthScore}/100 based on your analysis.`;
}


    // Finish animation
    if (circle) {
      circle.style.strokeDashoffset = '0';
    }

    if (percentNum) {
      percentNum.textContent = '100%';
    }

    if (stepKeywords) {
      stepKeywords.innerHTML = `
        <span class="font-medium">
          Checking keywords
        </span>
        ${checkSvg}
      `;
    }

    if (stepInsights) {
      stepInsights.classList.remove('opacity-60');

      stepInsights.innerHTML = `
        <span class="font-medium">
          Generating insights
        </span>
        ${checkSvg}
      `;
    }

    showToast(
      `AI analysis completed! Score: ${data.resume_score}/100`
    );

    // Small delay so user can see 100%
    setTimeout(() => {
      navigateTo('dashboard');
    }, 700);

  } catch (error) {

    console.error(
      'Resume analysis error:',
      error
    );

    showToast(
      error.message ||
      'Could not analyze the resume.',
      true
    );

    // Return to upload screen
    setTimeout(() => {
      navigateTo('upload');
    }, 1000);
  }
}

// =========================================================================
// AI SUGGESTIONS INTERACTION
// =========================================================================

/**
 * Filter suggestions by tag
 * @param {'all'|'critical'|'improvement'|'good'} category 
 */
function filterSuggestions(category) {
  const cards = document.querySelectorAll('#suggestionsContainer > div');
  cards.forEach(card => {
    const cardCat = card.getAttribute('data-category');
    if (category === 'all' || cardCat === category) {
      card.classList.remove('hidden');
    } else {
      card.classList.add('hidden');
    }
  });

  const buttons = ['all', 'critical', 'improvement', 'good'];
  buttons.forEach(btnName => {
    const btn = document.getElementById(`btnFilter${btnName.charAt(0).toUpperCase() + btnName.slice(1)}`);
    if (btn) {
      if (btnName === category) {
        btn.className = 'px-4 py-2 rounded-xl text-xs font-bold bg-indigo-500 text-white shadow-sm transition-all';
      } else {
        btn.className = 'px-4 py-2 rounded-xl text-xs font-bold bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-secondary)] hover:bg-[var(--bg-card-hover)] transition-all';
      }
    }
  });
}

/**
 * Interactively apply an AI suggestion to increase score & reduce issues count
 * @param {string} cardId 
 * @param {number} points 
 */
function applySuggestion(cardId, points) {
  if (appState.appliedSuggestions.has(cardId)) {
    showToast('This suggestion has already been applied!');
    return;
  }

  appState.appliedSuggestions.add(cardId);
  appState.resumeScore = Math.min(100, appState.resumeScore + points);
  appState.issuesCount = Math.max(0, appState.issuesCount - 1);

  // Update KPI counters on Dashboard
  const kpiScore = document.getElementById('kpiResumeScore');
  const kpiIssues = document.getElementById('kpiIssuesCount');
  const totalCount = document.getElementById('suggTotalCount');

  if (kpiScore) kpiScore.innerHTML = `${appState.resumeScore}<span class="text-xs text-[var(--text-muted)] font-normal">/100</span>`;
  // Update Resume Score progress circle
const resumeScoreCircle =
  document.getElementById('resumeScoreCircle');

if (resumeScoreCircle) {
  const score = Number(appState.resumeScore) || 0;

  resumeScoreCircle.setAttribute(
    'stroke-dasharray',
    `${score}, 100`
  );
}
  if (kpiIssues) kpiIssues.textContent = appState.issuesCount;
  if (totalCount) totalCount.textContent = appState.issuesCount;

  // Visual card updates
  const card = document.getElementById(cardId);
  if (card) {
    card.classList.add('opacity-75');
    const btn = card.querySelector('button');
    if (btn) {
      btn.textContent = 'Applied ✓';
      btn.className = 'py-2 px-5 rounded-full bg-emerald-500 text-white text-xs font-bold pointer-events-none';
    }
  }

  showToast(`Suggestion applied! Resume score increased to ${appState.resumeScore}/100 🚀`);
}

// =========================================================================
// JOB MATCH ANALYZER DYNAMICS
// =========================================================================
async function analyzeJobMatch() {

  const jobDescriptionInput =
    document.getElementById('jobDescriptionInput');

  const jobDescription =
    jobDescriptionInput?.value.trim();

  if (!jobDescription) {

    showToast(
      'Please paste a job description first.',
      true
    );

    return;
  }

  if (!selectedResumeFile) {

    showToast(
      'Please upload a resume first.',
      true
    );

    return;
  }

  try {

    const formData = new FormData();

    formData.append(
      'resume',
      selectedResumeFile
    );

    formData.append(
      'job_description',
      jobDescription
    );

    showToast(
      'Analyzing resume against the job description...'
    );

    const response = await fetch(
      'http://127.0.0.1:5000/api/resume/upload',
      {
        method: 'POST',
        body: formData
      }
    );

    const data = await response.json();

    if (!response.ok || !data.success) {

      throw new Error(
        data.message ||
        data.error ||
        'Job match analysis failed.'
      );
    }

    console.log("JOB MATCH DATA:", data.job_match);

    // Save latest analysis
    resumeAnalysisData = data;

    // Get job match result
    const jobMatch =
      data.job_match || {};
      console.log("JOB MATCH DATA:", data.job_match);

    const matchPercentage =
      jobMatch.match_percentage;

      // Update Dashboard Skills Match with Job Match result
const dashboardSkillsMatchCard =
  document.getElementById('kpiSkillsMatch');

const dashboardSkillsMatchCircle =
  document.getElementById('skillsMatchCircle');

const dashboardSkillsMatchStatus =
  document.getElementById('skillsMatchStatus');

if (
  matchPercentage !== null &&
  matchPercentage !== undefined
) {
  if (dashboardSkillsMatchCard) {
    dashboardSkillsMatchCard.textContent =
      `${matchPercentage}%`;
  }

  if (dashboardSkillsMatchCircle) {
    dashboardSkillsMatchCircle.setAttribute(
      'stroke-dasharray',
      `${Number(matchPercentage)}, 100`
    );
  }

  if (dashboardSkillsMatchStatus) {
    dashboardSkillsMatchStatus.textContent =
      'Analysis completed';
  }
}

      // Save latest Job Match percentage for Dashboard
if (
  matchPercentage !== null &&
  matchPercentage !== undefined
) {
  localStorage.setItem(
    'resumateJobMatchPercentage',
    matchPercentage
  );
}

    const matchedSkills =
      jobMatch.matched_skills || [];

    const missingSkills =
      jobMatch.missing_skills || [];

    
      
    // Update Skills Match progress circle
const skillsMatchCircle =
  document.getElementById('skillsMatchCircle');

if (skillsMatchCircle) {
  if (
    matchPercentage !== null &&
    matchPercentage !== undefined
  ) {
    skillsMatchCircle.setAttribute(
      'stroke-dasharray',
      `${Number(matchPercentage)}, 100`
    );
  } else {
    skillsMatchCircle.setAttribute(
      'stroke-dasharray',
      '0, 100'
    );
  }
}

        // ============================================================
    // UPDATE TOP STRENGTHS
    // ============================================================

    const topStrengthsList =
      document.getElementById('topStrengthsList');

    const topStrengthsButton =
      document.getElementById('topStrengthsButton');

    const topStrengths =
  resumeAnalysisData?.top_strengths ||
  data.top_strengths ||
  [];

    if (topStrengthsList) {

      // Clear old content
      topStrengthsList.innerHTML = '';

      if (topStrengths.length > 0) {

        topStrengths.forEach(item => {

          const strengthRow =
            document.createElement('div');

          strengthRow.className =
            'flex items-center gap-2.5 text-xs font-medium text-[var(--text-secondary)]';

          strengthRow.innerHTML = `
            <div class="w-5 h-5 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center shrink-0">
              <svg
                class="w-3.5 h-3.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2.5"
                  d="M5 13l4 4L19 7"
                ></path>
              </svg>
            </div>

            <span>${item.strength || 'Strength identified'}</span>
          `;

          topStrengthsList.appendChild(strengthRow);
        });

        // Show real strengths
        topStrengthsList.classList.remove('hidden');

        // Show button after analysis
        if (topStrengthsButton) {
          topStrengthsButton.classList.remove('hidden');
          topStrengthsButton.textContent =
            'View Improvement Suggestions';
        }

      } else {

        // Keep empty when there are no strengths
        topStrengthsList.classList.add('hidden');

        if (topStrengthsButton) {
          topStrengthsButton.classList.add('hidden');
        }
      }
    }

    // Update Job Match percentage
    const jobMatchPercent =
      document.getElementById('jobMatchPercent');

    if (jobMatchPercent) {

      jobMatchPercent.textContent =
        matchPercentage !== null &&
        matchPercentage !== undefined
          ? `${matchPercentage}%`
          : 'N/A';
    }

    // Update match rating and description
const jobMatchRating =
  document.getElementById('jobMatchRating');

const jobMatchDescription =
  document.getElementById('jobMatchDescription');

if (jobMatchRating) {

  let rating = 'Needs Improvement';

  if (matchPercentage >= 80) {
    rating = 'Great Match';
  } else if (matchPercentage >= 60) {
    rating = 'Good Match';
  } else if (matchPercentage >= 40) {
    rating = 'Partial Match';
  }

  jobMatchRating.textContent = rating;
}

if (jobMatchDescription) {

  jobMatchDescription.textContent =
    `Your resume matches ${matchPercentage}% of the required skills for this job.`;
}

    // Update Job Match circle
    const jobMatchCircle =
      document.getElementById('jobMatchCircle');

    if (
      jobMatchCircle &&
      matchPercentage !== null &&
      matchPercentage !== undefined
    ) {

      jobMatchCircle.setAttribute(
        'stroke-dasharray',
        `${matchPercentage}, 100`
      );
    }

    // Update Matching Skills
    const matchingContainer =
      document.getElementById(
        'matchingSkillsContainer'
      );

    if (matchingContainer) {

      matchingContainer.innerHTML =
        matchedSkills.length
          ? matchedSkills
              .map(
                skill =>
                  `<span class="skill-pill pill-match">${skill}</span>`
              )
              .join('')
          : '<span class="text-sm text-[var(--text-muted)]">No matching skills found.</span>';
    }

    // Update Missing Skills
    const missingContainer =
      document.getElementById(
        'missingSkillsContainer'
      );

    if (missingContainer) {

      missingContainer.innerHTML =
        missingSkills.length
          ? missingSkills
              .map(
                skill =>
                  `<span class="skill-pill pill-missing">${skill}</span>`
              )
              .join('')
          : '<span class="text-sm text-[var(--text-muted)]">No missing skills.</span>';
    }

    // Update skill counts
    const matchCount =
      document.getElementById(
        'matchSkillsCount'
      );

    if (matchCount) {

      matchCount.textContent =
        `${matchedSkills.length} skills`;
    }

    const missingCount =
      document.getElementById(
        'missingSkillsCount'
      );

    if (missingCount) {

      missingCount.textContent =
        `${missingSkills.length} skills`;
    }

    showToast(
      `Job match analysis completed! Match: ${matchPercentage}%`
    );

  } catch (error) {

    console.error(
      'Job match error:',
      error
    );

    showToast(
      error.message ||
      'Could not analyze job match.',
      true
    );
  }
}

const jobProfiles = {
  frontend: {
    title: 'Frontend Developer_JD.pdf',
    score: 87,
    rating: 'Great Match',
    ratingColor: 'text-emerald-500',
    matching: ['JavaScript', 'React', 'HTML', 'CSS', 'Git', 'Problem Solving'],
    missing: ['Next.js', 'TypeScript', 'AWS', 'Docker']
  },
  fullstack: {
    title: 'Fullstack_Software_Engineer_JD.pdf',
    score: 79,
    rating: 'Strong Match',
    ratingColor: 'text-cyan-500',
    matching: ['Python', 'JavaScript', 'SQL', 'Git', 'React', 'HTML/CSS'],
    missing: ['GraphQL', 'Kubernetes', 'Redis', 'CI/CD']
  },
  ai: {
    title: 'AI_ML_Engineer_JD.pdf',
    score: 73,
    rating: 'Good Match',
    ratingColor: 'text-indigo-500',
    matching: ['Python', 'SQL', 'Problem Solving', 'Data Analysis'],
    missing: ['PyTorch', 'TensorFlow', 'LLMs', 'MLOps', 'Vector DBs']
  }
};

function updateJobRole(roleKey) {
  const profile = jobProfiles[roleKey] || jobProfiles.frontend;
  const jdTitle = document.getElementById('jdTitle');
  const jobMatchPercent = document.getElementById('jobMatchPercent');
  const jobMatchRating = document.getElementById('jobMatchRating');
  const jobMatchCircle = document.getElementById('jobMatchCircle');
  const matchingContainer = document.getElementById('matchingSkillsContainer');
  const missingContainer = document.getElementById('missingSkillsContainer');
  const matchCount = document.getElementById('matchSkillsCount');
  const missingCount = document.getElementById('missingSkillsCount');

  if (jdTitle) jdTitle.textContent = profile.title;
  if (jobMatchPercent) jobMatchPercent.textContent = `${profile.score}%`;
  if (jobMatchRating) {
    jobMatchRating.textContent = profile.rating;
    jobMatchRating.className = `text-base font-bold ${profile.ratingColor}`;
  }
  if (jobMatchCircle) {
    jobMatchCircle.setAttribute('stroke-dasharray', `${profile.score}, 100`);
  }

  if (matchingContainer) {
    matchingContainer.innerHTML = profile.matching
      .map(skill => `<span class="skill-pill pill-match">${skill}</span>`)
      .join('');
  }
  if (missingContainer) {
    missingContainer.innerHTML = profile.missing
      .map(skill => `<span class="skill-pill pill-missing">${skill}</span>`)
      .join('');
  }

  if (matchCount) matchCount.textContent = `${profile.matching.length} skills`;
  if (missingCount) missingCount.textContent = `${profile.missing.length} skills`;

  showToast(`Updated analysis for role: ${profile.title.replace('_JD.pdf', '')}`);
}

// =========================================================================
// REPORT EXPORT & SHARE MODAL
// =========================================================================

async function downloadReport() {

  if (!resumeAnalysisData) {
    showToast(
      'Please analyze a resume before downloading the report.',
      true
    );
    return;
  }

  try {

    const response = await fetch(
      'http://127.0.0.1:5000/api/analysis/download-report',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(resumeAnalysisData)
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      throw new Error(
        errorData.message ||
        errorData.error ||
        'Could not download the report.'
      );
    }

    const blob = await response.blob();

    const url = window.URL.createObjectURL(blob);

    const link = document.createElement('a');

    link.href = url;

    link.download = 'ResuMate_Resume_Report.pdf';

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    window.URL.revokeObjectURL(url);

    showToast(
      'Resume analysis PDF downloaded successfully! 📄'
    );

  } catch (error) {

    console.error(
      'Report download error:',
      error
    );

    showToast(
      error.message ||
      'Could not download the report.',
      true
    );
  }
}

function shareReport() {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(window.location.href);
    showToast('Shareable link copied to clipboard!');
  } else {
    showToast('Share link ready: ' + window.location.href);
  }
}

function showHelpModal() {
    const existingModal = document.getElementById("helpModal");

    if (existingModal) {
        existingModal.remove();
        return;
    }

    const modal = document.createElement("div");

    modal.id = "helpModal";

    modal.className =
        "fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4";

    modal.innerHTML = `
        <div class="w-full max-w-lg resumate-card shadow-2xl border border-indigo-500/20 overflow-hidden">

            <div class="flex items-center justify-between px-6 py-5 border-b border-[var(--border-color)]">
                <div>
                    <h2 class="text-lg font-bold text-[var(--text-primary)]">
                        ResuMate Quick Guide
                    </h2>
                    <p class="text-sm text-[var(--text-muted)] mt-1">
                        Get the most out of your resume analysis.
                    </p>
                </div>

                <button
                    onclick="document.getElementById('helpModal').remove()"
                    class="w-8 h-8 rounded-lg flex items-center justify-center text-[var(--text-secondary)] hover:bg-[var(--bg-card-hover)] transition-colors text-xl"
                    title="Close"
                >
                    ×
                </button>
            </div>

            <div class="px-6 py-5 space-y-4">

                <div class="flex gap-3">
                    <div class="w-9 h-9 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center shrink-0">
                        ☀️
                    </div>
                    <div>
                        <h3 class="text-sm font-semibold text-[var(--text-primary)]">
                            Switch themes
                        </h3>
                        <p class="text-sm text-[var(--text-muted)] mt-1">
                            Switch between light and dark mode using the theme toggle.
                        </p>
                    </div>
                </div>

                <div class="flex gap-3">
                    <div class="w-9 h-9 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center shrink-0">
                        📊
                    </div>
                    <div>
                        <h3 class="text-sm font-semibold text-[var(--text-primary)]">
                            Explore your analysis
                        </h3>
                        <p class="text-sm text-[var(--text-muted)] mt-1">
                            Use the sidebar to explore your resume score, skills, suggestions, and section analysis.
                        </p>
                    </div>
                </div>

                <div class="flex gap-3">
                    <div class="w-9 h-9 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center shrink-0">
                        📄
                    </div>
                    <div>
                        <h3 class="text-sm font-semibold text-[var(--text-primary)]">
                            Analyze your resume
                        </h3>
                        <p class="text-sm text-[var(--text-muted)] mt-1">
                            Upload your resume or click Analyze New Resume to start your analysis.
                        </p>
                    </div>
                </div>

                <div class="flex gap-3">
                    <div class="w-9 h-9 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center shrink-0">
                        ✨
                    </div>
                    <div>
                        <h3 class="text-sm font-semibold text-[var(--text-primary)]">
                            Improve your resume
                        </h3>
                        <p class="text-sm text-[var(--text-muted)] mt-1">
                            Review your suggestions and apply improvements to strengthen your resume.
                        </p>
                    </div>
                </div>

            </div>

            <div class="px-6 py-4 border-t border-[var(--border-color)] flex justify-end">
                <button
                    onclick="document.getElementById('helpModal').remove()"
                    class="px-5 py-2.5 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-sm font-semibold hover:opacity-90 transition-opacity"
                >
                    Got it
                </button>
            </div>

        </div>
    `;

    document.body.appendChild(modal);

    modal.addEventListener("click", function(event) {
        if (event.target === modal) {
            modal.remove();
        }
    });
}

// =========================================================================
// TOAST NOTIFICATION UTILITY
// =========================================================================

let toastTimeout;
function showToast(message, isError = false) {
  const toast = document.getElementById('toastNotification');
  const toastMessage = document.getElementById('toastMessage');
  const toastIcon = document.getElementById('toastIcon');

  if (!toast || !toastMessage) return;

  clearTimeout(toastTimeout);

  toastMessage.textContent = message;
  if (isError) {
    toastIcon.textContent = '✕';
    toastIcon.className = 'w-6 h-6 rounded-full bg-red-500/20 text-red-500 flex items-center justify-center text-xs font-bold';
  } else {
    toastIcon.textContent = '✓';
    toastIcon.className = 'w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center text-xs font-bold';
  }

  toast.classList.remove('translate-y-20', 'opacity-0');
  toast.classList.add('translate-y-0', 'opacity-100');

  toastTimeout = setTimeout(() => {
    toast.classList.add('translate-y-20', 'opacity-0');
    toast.classList.remove('translate-y-0', 'opacity-100');
  }, 3200);
}

// =========================================================================
// INITIALIZATION ON DOM LOAD
// =========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initializeTheme();

  // Drag and drop listeners on dropzone
  const dropzone = document.getElementById('dropzone');
  if (dropzone) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      }, false);
    });

    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length) {
        handleFileSelected({ target: { files: files } });
      }
    }, false);
  }
});

function showProfileModal() {
    const existingModal = document.getElementById("profileModal");

    if (existingModal) {
        existingModal.remove();
        return;
    }

    const modal = document.createElement("div");

    modal.id = "profileModal";

    modal.className =
        "fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4";

    modal.innerHTML = `
        <div class="w-full max-w-md resumate-card shadow-2xl border border-indigo-500/20 overflow-hidden">

            <div class="flex items-center justify-between px-6 py-5 border-b border-[var(--border-color)]">
                <div>
                    <h2 class="text-lg font-bold text-[var(--text-primary)]">
                        My Profile
                    </h2>
                    <p class="text-sm text-[var(--text-muted)] mt-1">
                        View and manage your ResuMate profile.
                    </p>
                </div>

                <button
                    onclick="document.getElementById('profileModal').remove()"
                    class="w-8 h-8 rounded-lg flex items-center justify-center text-[var(--text-secondary)] hover:bg-[var(--bg-card-hover)] transition-colors text-xl"
                    title="Close"
                >
                    ×
                </button>
            </div>

            <div class="px-6 py-6">

                <div class="flex flex-col items-center mb-6">
                    <div class="w-20 h-20 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                        R
                    </div>

                    <h3 class="mt-3 text-base font-bold text-[var(--text-primary)]">
                        ${document.getElementById("userNameDisplay")?.textContent || "User"}
                    </h3>

                    <p class="text-sm text-[var(--text-muted)]">
                        ResuMate User
                    </p>
                </div>

                <div class="space-y-4">

                    <div>
                        <label class="block text-xs font-semibold text-[var(--text-secondary)] mb-1.5">
                            Full Name
                        </label>
                        <input
                            id="profileNameInput"
                            type="text"
                            value="${document.getElementById("userNameDisplay")?.textContent || ""}"
                            class="w-full px-4 py-3 rounded-lg bg-[var(--bg-card-hover)] border border-[var(--border-color)] text-sm text-[var(--text-primary)] outline-none focus:border-indigo-500"
                        >
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-[var(--text-secondary)] mb-1.5">
                            Email
                        </label>
                        <input
                            type="email"
                            placeholder="Your registered email"
                            class="w-full px-4 py-3 rounded-lg bg-[var(--bg-card-hover)] border border-[var(--border-color)] text-sm text-[var(--text-primary)] outline-none focus:border-indigo-500"
                        >
                    </div>

                </div>

            </div>

            <div class="px-6 py-4 border-t border-[var(--border-color)] flex justify-end gap-3">

                <button
                    onclick="document.getElementById('profileModal').remove()"
                    class="px-4 py-2.5 rounded-lg border border-[var(--border-color)] text-sm font-semibold text-[var(--text-secondary)] hover:bg-[var(--bg-card-hover)]"
                >
                    Cancel
                </button>

                <button
                    onclick="saveProfileChanges()"
                    class="px-5 py-2.5 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-sm font-semibold hover:opacity-90"
                >
                    Save Changes
                </button>

            </div>

        </div>
    `;

    document.body.appendChild(modal);

    modal.addEventListener("click", function(event) {
        if (event.target === modal) {
            modal.remove();
        }
    });
}
function saveProfileChanges() {
    const nameInput = document.getElementById("profileNameInput");

    if (!nameInput) return;

    const newName = nameInput.value.trim();

    if (!newName) {
        alert("Please enter your name.");
        return;
    }

    // Update the name in the dashboard header
    const userNameDisplay = document.getElementById("userNameDisplay");

    if (userNameDisplay) {
        userNameDisplay.textContent = newName;
    }

    // Update dashboard greeting
    const dashboardGreeting = document.getElementById("dashboardGreeting");

    if (dashboardGreeting) {
        dashboardGreeting.textContent = `Hello, ${newName} 👋`;
    }

    // Close profile modal
    const modal = document.getElementById("profileModal");

    if (modal) {
        modal.remove();
    }

    // Show success message
    if (typeof showToast === "function") {
        showToast("Profile updated successfully.");
    } else {
        alert("Profile updated successfully.");
    }
}

function toggleChatbot() {
    const chatbotWindow =
        document.getElementById('chatbotWindow');

    const greeting =
        document.getElementById('chatbotGreeting');

        const suggestions =
    document.getElementById('chatbotSuggestions');

     if (!chatbotWindow) return;
     
if (suggestions) {
    suggestions.classList.remove('hidden');
}

    // Hide greeting
    if (greeting) {
        greeting.classList.add('hidden');
    }

    // Open chatbot
    chatbotWindow.classList.remove('hidden');
}
function closeChatbot() {
    const chatbotWindow =
        document.getElementById('chatbotWindow');

    if (chatbotWindow) {
        chatbotWindow.classList.add('hidden');
    }
}
async function sendChatbotMessage() {
    const input =
        document.getElementById('chatbotInput');

    const messages =
        document.getElementById('chatbotMessages');

    if (!input || !messages) return;

    const userMessage =
        input.value.trim();

    if (!userMessage) return;

    const suggestions =
    document.getElementById('chatbotSuggestions');

if (suggestions) {
    suggestions.classList.add('hidden');
}

    // Show user's message
    const userBubble =
        document.createElement('div');

    userBubble.className =
        'flex justify-end';

    userBubble.innerHTML = `
        <div class="max-w-[80%] rounded-2xl rounded-tr-sm px-3 py-2 bg-indigo-500 text-white text-sm">
            ${userMessage}
        </div>
    `;

    messages.appendChild(userBubble);

    // Clear input
    input.value = '';

    // Scroll to bottom
    messages.scrollTop =
        messages.scrollHeight;

        // Show typing indicator
const typingBubble =
    document.createElement('div');

typingBubble.id =
    'chatbotTyping';

typingBubble.className =
    'flex items-start gap-2';

typingBubble.innerHTML = `
    <img
        src="../assets/chatbot.jpeg"
        class="w-8 h-8 rounded-full object-contain"
        alt="AI"
    >

    <div class="rounded-2xl rounded-tl-sm px-3 py-2 bg-[var(--bg-card-hover)] text-sm text-[var(--text-muted)]">
        ResuMate AI is typing...
    </div>
`;

messages.appendChild(typingBubble);

messages.scrollTop =
    messages.scrollHeight;
    
    

    try {
        const response =
            await fetch(
                'http://127.0.0.1:5000/api/chatbot/chat',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type':
                            'application/json'
                    },
                    body: JSON.stringify({
                        message: userMessage,
                        resume_data:
                            resumeAnalysisData || null
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message ||
                'Chatbot request failed.'
            );
        }

        // Keep typing indicator visible briefly
await new Promise(resolve =>
    setTimeout(resolve, 800)
);

        const typingIndicator =
    document.getElementById('chatbotTyping');

if (typingIndicator) {
    typingIndicator.remove();
}

        // Show AI response
        const aiBubble =
            document.createElement('div');

        aiBubble.className =
            'flex items-start gap-2';

        aiBubble.innerHTML = `
            <img
                src="../assets/chatbot.jpeg"
                class="w-8 h-8 rounded-full object-contain"
                alt="AI"
            >

            <div class="max-w-[80%] rounded-2xl rounded-tl-sm px-3 py-2 bg-[var(--bg-card-hover)] text-sm text-[var(--text-primary)]">
                ${data.response}
            </div>
        `;

        messages.appendChild(aiBubble);

        messages.scrollTop =
            messages.scrollHeight;

    } catch (error) {

        console.error(
            'Chatbot error:',
            error
        );

        const errorBubble =
            document.createElement('div');

        errorBubble.className =
            'text-xs text-red-400 px-2';

        errorBubble.textContent =
            'Sorry, I could not connect to the chatbot.';

        messages.appendChild(errorBubble);
    }
}


