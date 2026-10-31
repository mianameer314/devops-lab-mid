document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("submission-form");
    const alertBox = document.getElementById("alert-box");
    const tbody = document.getElementById("submissions-tbody");
    const counter = document.getElementById("submission-counter");
    const resetBtn = document.getElementById("reset-btn");

    // Fetch existing submissions on load
    loadSubmissions();

    // Form submission handler
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        hideAlert();

        const student_name = document.getElementById("student_name").value.trim();
        const reg_no = document.getElementById("reg_no").value.trim();
        const assignment_title = document.getElementById("assignment_title").value.trim();
        const submission_url = document.getElementById("submission_url").value.trim();

        // Basic client-side pre-validation
        if (!student_name) {
            showAlert("Student name is required.", "error");
            return;
        }
        if (!reg_no) {
            showAlert("Missing registration number. Registration number is required.", "error");
            return;
        }
        if (!assignment_title) {
            showAlert("Assignment title is required.", "error");
            return;
        }
        if (!submission_url) {
            showAlert("Submission URL is required.", "error");
            return;
        }

        const payload = {
            student_name,
            reg_no,
            assignment_title,
            submission_url
        };

        try {
            const response = await fetch("/api/submissions", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (response.status === 201) {
                showAlert(data.message || "The submission is saved and appears in the submission list.", "success");
                form.reset();
                loadSubmissions();
            } else {
                showAlert(data.message || "Validation failed.", "error");
            }
        } catch (err) {
            // Static mode fallback (e.g. for GitHub Pages demo)
            handleStaticFallbackSubmission(payload);
        }
    });

    resetBtn.addEventListener("click", () => {
        form.reset();
        hideAlert();
    });

    async function loadSubmissions() {
        try {
            const response = await fetch("/api/submissions");
            if (!response.ok) throw new Error("API unavailable");
            const data = await response.json();
            renderTable(data.submissions || []);
        } catch (err) {
            // Load from localStorage if API is not available (Static GitHub Pages mode)
            const local = JSON.parse(localStorage.getItem("devops_submissions") || "[]");
            renderTable(local);
        }
    }

    function renderTable(submissions) {
        counter.textContent = `${submissions.length} Submission${submissions.length === 1 ? '' : 's'}`;

        if (submissions.length === 0) {
            tbody.innerHTML = `
                <tr id="empty-row">
                    <td colspan="6" class="text-center text-muted">No submissions recorded yet. Submit the form above to add a record.</td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = submissions.map((sub, index) => {
            const formattedDate = sub.submitted_at 
                ? new Date(sub.submitted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) 
                : 'Just now';
            return `
                <tr>
                    <td>${sub.id || (index + 1)}</td>
                    <td><strong>${escapeHtml(sub.student_name)}</strong></td>
                    <td><code>${escapeHtml(sub.reg_no)}</code></td>
                    <td>${escapeHtml(sub.assignment_title)}</td>
                    <td><a href="${escapeHtml(sub.submission_url)}" target="_blank" rel="noopener noreferrer" class="sub-link">${escapeHtml(sub.submission_url)}</a></td>
                    <td><small class="text-muted">${formattedDate}</small></td>
                </tr>
            `;
        }).join("");
    }

    function handleStaticFallbackSubmission(payload) {
        // Validate URL format locally in static demo mode
        if (!payload.submission_url.startsWith("http://") && !payload.submission_url.startsWith("https://")) {
            showAlert("Invalid submission URL. Must be a valid HTTP or HTTPS URL.", "error");
            return;
        }

        const local = JSON.parse(localStorage.getItem("devops_submissions") || "[]");
        const newRecord = {
            id: local.length + 1,
            ...payload,
            submitted_at: new Date().toISOString()
        };
        local.push(newRecord);
        localStorage.setItem("devops_submissions", JSON.stringify(local));
        showAlert("The submission is saved and appears in the submission list. (Static Demo Mode)", "success");
        form.reset();
        renderTable(local);
    }

    function showAlert(message, type) {
        alertBox.textContent = message;
        alertBox.className = `alert ${type}`;
    }

    function hideAlert() {
        alertBox.className = "alert hidden";
        alertBox.textContent = "";
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text || "";
        return div.innerHTML;
    }
});

