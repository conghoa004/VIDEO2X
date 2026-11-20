/**
 * Video2X Web UI Studio Controller (Vanilla JavaScript)
 * Quản lý tương tác DOM, Tải lên video, Cấu hình Preset 1-Click, 
 * SSE Live Progress & Logs, Video Stream và Phím tắt.
 */

let selectedFilePath = "";
let selectedFileName = "";
let outputFileName = "";
let currentTaskMode = "realesrgan";
let currentScale = 4;
let currentRifeMul = 2;
let sseEventSource = null;
let autoScrollLogs = true;
let currentPlayerTab = "output";

// ==========================================
// 1. KHỞI TẠO VÀ LOAD TRẠNG THÁI HỆ THỐNG
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    fetchSystemEnvironment();
    fetchGpuStatus();
    connectSSE();
    setupDropzone();
    setupKeyboardShortcuts();
});

async function fetchSystemEnvironment() {
    try {
        const res = await fetch("/api/system/env");
        if (res.ok) {
            const data = await res.json();
            const vulkanText = document.getElementById("vulkan-text");
            const diskText = document.getElementById("disk-text");

            if (vulkanText) {
                if (data.vulkan) {
                    vulkanText.innerText = data.vulkan_device || "Vulkan Ready";
                    vulkanText.classList.remove("text-slate-300", "text-rose-400", "text-amber-400");
                    vulkanText.classList.add("text-emerald-400");
                } else {
                    vulkanText.innerText = data.vulkan_device ? `Vulkan: ${data.vulkan_device}` : "Vulkan Chưa sẵn sàng";
                    vulkanText.classList.remove("text-slate-300", "text-emerald-400");
                    vulkanText.classList.add("text-amber-400");
                }
            }

            if (diskText && data.disk_free_gb) {
                diskText.innerText = `Disk: ${data.disk_free_gb} GB trống`;
            }
        }
    } catch (e) {
        console.error("Lỗi lấy thông tin env:", e);
    }
}

async function fetchGpuStatus() {
    try {
        const res = await fetch("/api/system/gpu");
        if (res.ok) {
            const data = await res.json();
            const gpuText = document.getElementById("gpu-text");
            if (gpuText) {
                gpuText.innerText = data.available ? `${data.name} (${data.driver_ver})` : "Không tìm thấy GPU";
            }
            
            // Calculate VRAM percentage
            let vramPct = 0;
            const usedMatch = (data.vram_used || "").match(/(\d+)/);
            const totalMatch = (data.vram_total || "").match(/(\d+)/);
            if (usedMatch && totalMatch) {
                const used = parseFloat(usedMatch[1]);
                const total = parseFloat(totalMatch[1]);
                if (total > 0) {
                    vramPct = Math.round((used / total) * 100);
                }
            }

            // Update modal fields
            const mName = document.getElementById("modal-gpu-name");
            const mDriver = document.getElementById("modal-gpu-driver");
            const mVram = document.getElementById("modal-gpu-vram");
            const mTemp = document.getElementById("modal-gpu-temp");
            const mUtil = document.getElementById("modal-gpu-util");
            const mPower = document.getElementById("modal-gpu-power");
            const mVramBar = document.getElementById("modal-gpu-vram-bar");
            const mVramPct = document.getElementById("modal-gpu-vram-pct");
            const mStatus = document.getElementById("modal-gpu-status-text");

            if (mName) mName.innerText = data.name;
            if (mDriver) mDriver.innerText = data.driver_ver;
            if (mVram) mVram.innerText = `${data.vram_used} / ${data.vram_total}`;
            if (mTemp) mTemp.innerText = data.temperature;
            if (mUtil) mUtil.innerText = data.gpu_util || "0%";
            if (mPower) mPower.innerText = data.power || "N/A";
            if (mVramBar) mVramBar.style.width = vramPct + "%";
            if (mVramPct) mVramPct.innerText = vramPct + "%";
            if (mStatus) mStatus.innerText = data.available ? "Đang hoạt động" : "Không tìm thấy GPU";
        }
    } catch (e) {
        console.error("Lỗi lấy thông tin GPU:", e);
    }
}

// ==========================================
// 2. 1-CLICK PRESETS
// ==========================================
function applyPreset(preset) {
    if (preset === "anime_hq") {
        selectTaskMode("realesrgan");
        document.getElementById("realesrgan-model").value = "realesr-animevideov3";
        setScale(4);
        document.getElementById("encoder-codec").value = "libx264";
        document.getElementById("encoder-preset").value = "slow";
        document.getElementById("encoder-crf").value = 18;
        updateCrfLabel(18);
        appendTerminalLog("[Preset] Đã áp dụng cấu hình: Anime 4K (Real-ESRGAN v3 + 4x + CRF 18)");
    } else if (preset === "anime_fast") {
        selectTaskMode("libplacebo");
        document.getElementById("anime4k-shader").value = "anime4k-v4-a";
        document.getElementById("encoder-codec").value = "libx264";
        document.getElementById("encoder-preset").value = "fast";
        document.getElementById("encoder-crf").value = 18;
        updateCrfLabel(18);
        appendTerminalLog("[Preset] Đã áp dụng cấu hình: Anime Siêu Tốc (Anime4K Shaders)");
    } else if (preset === "real_life") {
        selectTaskMode("realesrgan");
        document.getElementById("realesrgan-model").value = "realesrgan-plus";
        setScale(4);
        document.getElementById("encoder-codec").value = "libx264";
        document.getElementById("encoder-preset").value = "slow";
        document.getElementById("encoder-crf").value = 16;
        updateCrfLabel(16);
        appendTerminalLog("[Preset] Đã áp dụng cấu hình: Đời Thực 4K (Real-ESRGAN Plus + 4x + CRF 16)");
    } else if (preset === "rife_60fps") {
        selectTaskMode("rife");
        document.getElementById("rife-model").value = "rife-v4.6";
        setRifeMul(2);
        document.getElementById("encoder-codec").value = "libx264";
        document.getElementById("encoder-preset").value = "medium";
        document.getElementById("encoder-crf").value = 18;
        updateCrfLabel(18);
        appendTerminalLog("[Preset] Đã áp dụng cấu hình: Tăng 60 FPS Mượt (RIFE v4.6 Optical Flow)");
    }
}

// ==========================================
// 3. QUẢN LÝ CHỌN / TẢI VIDEO
// ==========================================
function switchInputMode(mode) {
    const uploadBtn = document.getElementById("tab-btn-upload");
    const pathBtn = document.getElementById("tab-btn-path");
    const uploadSec = document.getElementById("input-section-upload");
    const pathSec = document.getElementById("input-section-path");

    if (mode === "upload") {
        uploadBtn.className = "px-3 py-1 rounded-lg bg-accent-600 text-white font-semibold transition shadow-sm";
        pathBtn.className = "px-3 py-1 rounded-lg text-slate-400 hover:text-white transition";
        uploadSec.classList.remove("hidden");
        pathSec.classList.add("hidden");
    } else {
        pathBtn.className = "px-3 py-1 rounded-lg bg-accent-600 text-white font-semibold transition shadow-sm";
        uploadBtn.className = "px-3 py-1 rounded-lg text-slate-400 hover:text-white transition";
        pathSec.classList.remove("hidden");
        uploadSec.classList.add("hidden");
    }
}

function setupDropzone() {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("video-file-input");

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("border-accent-500", "bg-slate-900/90", "scale-[1.01]");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("border-accent-500", "bg-slate-900/90", "scale-[1.01]");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("border-accent-500", "bg-slate-900/90", "scale-[1.01]");
        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });
}

function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        uploadFile(e.target.files[0]);
    }
}

function uploadFile(file) {
    const container = document.getElementById("upload-progress-container");
    const bar = document.getElementById("upload-progress-bar");
    const percentText = document.getElementById("upload-percent");
    const filenameText = document.getElementById("upload-filename");

    container.classList.remove("hidden");
    filenameText.innerText = file.name;
    bar.style.width = "0%";
    percentText.innerText = "0%";

    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append("file", file);

    xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable) {
            const p = Math.round((e.loaded / e.total) * 100);
            bar.style.width = p + "%";
            percentText.innerText = p + "%";
        }
    });

    xhr.onload = () => {
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            displaySelectedVideo(data);
            setTimeout(() => container.classList.add("hidden"), 1000);
        } else {
            alert("Lỗi khi tải file lên: " + xhr.responseText);
            container.classList.add("hidden");
        }
    };

    xhr.onerror = () => {
        alert("Lỗi kết nối khi tải file.");
        container.classList.add("hidden");
    };

    xhr.open("POST", "/api/video/upload");
    xhr.send(formData);
}

async function probeVideoPath() {
    const input = document.getElementById("dataset-filepath-input");
    const path = input.value.trim();
    if (!path) {
        alert("Vui lòng nhập đường dẫn file video!");
        return;
    }

    try {
        const res = await fetch("/api/video/probe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filepath: path })
        });
        if (res.ok) {
            const data = await res.json();
            displaySelectedVideo(data);
        } else {
            const err = await res.json();
            alert("Không tìm thấy file: " + (err.detail || ""));
        }
    } catch (e) {
        alert("Lỗi khi kiểm tra đường dẫn: " + e);
    }
}

function displaySelectedVideo(meta) {
    selectedFilePath = meta.filepath;
    selectedFileName = meta.filename;
    const card = document.getElementById("video-meta-card");
    document.getElementById("meta-filename").innerText = meta.filename;
    document.getElementById("meta-filepath").innerText = meta.filepath;
    document.getElementById("meta-res").innerText = meta.resolution;
    document.getElementById("meta-fps").innerText = meta.fps;
    document.getElementById("meta-dur").innerText = meta.duration;
    document.getElementById("meta-size").innerText = meta.size_mb + " MB";
    card.classList.remove("hidden");
    lucide.createIcons();
    appendTerminalLog(`[Đầu vào] Đã chọn video: ${meta.filename} (${meta.resolution}, ${meta.fps})`);
}

function clearSelectedVideo() {
    selectedFilePath = "";
    selectedFileName = "";
    document.getElementById("video-meta-card").classList.add("hidden");
    document.getElementById("dataset-filepath-input").value = "";
    document.getElementById("video-file-input").value = "";
}

function previewSourceVideo() {
    if (!selectedFilePath) return;
    const player = document.getElementById("result-video-player");
    const placeholder = document.getElementById("video-placeholder");
    const streamUrl = `/api/video/stream/${encodeURIComponent(selectedFileName)}?type=input`;

    player.src = streamUrl;
    player.classList.remove("hidden");
    placeholder.classList.add("hidden");
    player.play();
}

// ==========================================
// 4. ĐIỀU KHIỂN CHẾ ĐỘ & MÔ HÌNH AI
// ==========================================
function selectTaskMode(mode) {
    currentTaskMode = mode;
    const modes = ["realesrgan", "libplacebo", "rife"];

    modes.forEach((m) => {
        const btn = document.getElementById(`mode-btn-${m}`);
        const group = document.getElementById(`group-${m}`);
        if (m === mode) {
            btn.className = "py-2.5 rounded-lg bg-accent-600 text-white transition text-center flex flex-col items-center shadow-sm";
            group.classList.remove("hidden");
        } else {
            btn.className = "py-2.5 rounded-lg text-slate-400 hover:text-white transition text-center flex flex-col items-center";
            group.classList.add("hidden");
        }
    });
}

function setScale(val) {
    currentScale = val;
    document.getElementById("scale-badge").innerText = val + "x";
    document.querySelectorAll(".scale-btn").forEach((b) => {
        if (parseInt(b.dataset.scale) === val) {
            b.className = "scale-btn py-2 rounded-xl border border-accent-500/80 bg-accent-600/20 text-xs font-bold text-accent-400 transition";
        } else {
            b.className = "scale-btn py-2 rounded-xl border border-slate-800 bg-slate-950 text-xs font-semibold text-slate-300 hover:border-slate-700 transition";
        }
    });
}

function setRifeMul(val) {
    currentRifeMul = val;
    document.querySelectorAll(".rife-mul-btn").forEach((b) => {
        if (parseInt(b.dataset.mul) === val) {
            b.className = "rife-mul-btn py-2 rounded-xl border border-accent-500 bg-accent-600/20 text-xs font-bold text-accent-400";
        } else {
            b.className = "rife-mul-btn py-2 rounded-xl border border-slate-800 bg-slate-950 text-xs font-semibold text-slate-300";
        }
    });
}

function updateCrfLabel(val) {
    const badge = document.getElementById("crf-value-badge");
    let label = "Đẹp chuẩn";
    if (val <= 16) label = "Gần Lossless";
    else if (val >= 24) label = "Nén sâu";
    badge.innerText = `${val} (${label})`;
}

function toggleAccordion(id) {
    const el = document.getElementById(id);
    const icon = document.getElementById(`accordion-icon-${id}`);
    if (el.classList.contains("hidden")) {
        el.classList.remove("hidden");
        icon.classList.add("rotate-180");
    } else {
        el.classList.add("hidden");
        icon.classList.remove("rotate-180");
    }
}

// ==========================================
// 5. TIẾN TRÌNH & SERVER-SENT EVENTS (SSE)
// ==========================================
function connectSSE() {
    if (sseEventSource) {
        sseEventSource.close();
    }

    sseEventSource = new EventSource("/api/tasks/stream");

    sseEventSource.addEventListener("progress", (e) => {
        const p = JSON.parse(e.data);
        updateProgressUI(p);
    });

    sseEventSource.addEventListener("log", (e) => {
        const d = JSON.parse(e.data);
        appendTerminalLog(d.text);
    });

    sseEventSource.addEventListener("complete", (e) => {
        const r = JSON.parse(e.data);
        onTaskComplete(r);
    });

    sseEventSource.addEventListener("error", (e) => {
        if (e.data) {
            try {
                const err = JSON.parse(e.data);
                appendTerminalLog("❌ Lỗi: " + (err.message || "Tiến trình thất bại"));
                setProcessingState(false);
                const banner = document.getElementById("status-banner");
                banner.className = "mt-4 p-3.5 rounded-xl bg-red-950/40 border border-red-900/60 text-xs text-red-300 flex items-center space-x-2.5";
                document.getElementById("status-banner-text").innerText = err.message || "Lỗi xử lý";
            } catch (_) {}
        }
    });
}

function updateProgressUI(p) {
    setProcessingState(true);
    document.getElementById("main-progress-bar").style.width = p.percent + "%";
    document.getElementById("progress-percent-badge").innerText = p.percent.toFixed(1) + "%";
    document.getElementById("stat-frames").innerText = `${p.current_frame.toLocaleString()} / ${p.total_frames.toLocaleString()}`;
    document.getElementById("stat-fps").innerText = p.fps + " FPS";
    document.getElementById("stat-elapsed").innerText = p.elapsed;
    document.getElementById("stat-remaining").innerText = p.remaining;

    const banner = document.getElementById("status-banner");
    banner.className = "mt-4 p-3.5 rounded-xl bg-accent-950/40 border border-accent-900/60 text-xs text-accent-300 flex items-center space-x-2.5";
    document.getElementById("status-banner-text").innerText = p.status_text;

    // Header live pill
    const headerStatus = document.getElementById("header-status-text");
    if (headerStatus) {
        headerStatus.innerText = `Đang xử lý ${p.percent.toFixed(0)}%`;
    }
}

function appendTerminalLog(text) {
    const logsEl = document.getElementById("terminal-logs");
    const p = document.createElement("p");
    p.textContent = text;
    logsEl.appendChild(p);

    if (autoScrollLogs) {
        logsEl.scrollTop = logsEl.scrollHeight;
    }
}

function clearLogs() {
    document.getElementById("terminal-logs").innerHTML = "";
}

function copyLogs() {
    const logsEl = document.getElementById("terminal-logs");
    const text = logsEl.innerText;
    navigator.clipboard.writeText(text).then(() => {
        const textSpan = document.getElementById("copy-log-text");
        if (textSpan) {
            textSpan.innerText = "Đã chép!";
            setTimeout(() => { textSpan.innerText = "Sao chép"; }, 1500);
        }
    });
}

function toggleAutoScroll() {
    autoScrollLogs = !autoScrollLogs;
    const btn = document.getElementById("btn-toggle-scroll");
    const dot = document.getElementById("scroll-dot");
    if (autoScrollLogs) {
        btn.querySelector("span:last-child").innerText = "Tự cuộn: BẬT";
        dot.className = "w-1.5 h-1.5 rounded-full bg-emerald-400";
    } else {
        btn.querySelector("span:last-child").innerText = "Tự cuộn: TẮT";
        dot.className = "w-1.5 h-1.5 rounded-full bg-slate-500";
    }
}

async function startProcessing() {
    if (!selectedFilePath) {
        alert("Vui lòng chọn hoặc tải lên một file video trước!");
        return;
    }

    const payload = {
        input_file: selectedFilePath,
        task_mode: currentTaskMode,
        realesrgan_model: document.getElementById("realesrgan-model").value,
        scale_factor: currentScale,
        shader_name: document.getElementById("anime4k-shader").value,
        target_width: parseInt(document.getElementById("target-width").value) || 0,
        target_height: parseInt(document.getElementById("target-height").value) || 0,
        rife_model: document.getElementById("rife-model").value,
        frame_rate_mul: currentRifeMul,
        codec: document.getElementById("encoder-codec").value,
        preset: document.getElementById("encoder-preset").value,
        crf: parseInt(document.getElementById("encoder-crf").value) || 18,
        pixfmt: document.getElementById("encoder-pixfmt").value,
        bitrate: parseInt(document.getElementById("encoder-bitrate").value) || 0
    };

    try {
        setProcessingState(true);
        const res = await fetch("/api/tasks/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            alert("Lỗi: " + (err.detail || "Không thể khởi động"));
            setProcessingState(false);
        }
    } catch (e) {
        alert("Lỗi kết nối khi gửi lệnh khởi chạy: " + e);
        setProcessingState(false);
    }
}

async function abortProcessing() {
    if (!confirm("Bạn có chắc chắn muốn hủy tiến trình đang chạy?")) return;
    try {
        await fetch("/api/tasks/abort", { method: "POST" });
    } catch (e) {
        console.error("Lỗi khi gửi lệnh hủy:", e);
    }
}

function setProcessingState(running) {
    const btnStart = document.getElementById("btn-start");
    const btnAbort = document.getElementById("btn-abort");
    const headerPill = document.getElementById("badge-status-pill");
    const headerStatus = document.getElementById("header-status-text");

    if (running) {
        btnStart.disabled = true;
        btnStart.className = "flex-1 py-4 px-6 rounded-2xl bg-slate-800 text-slate-500 font-bold text-sm cursor-not-allowed flex items-center justify-center space-x-2";
        btnAbort.disabled = false;
        btnAbort.className = "py-4 px-6 rounded-2xl bg-red-600 hover:bg-red-500 text-white font-bold text-sm flex items-center justify-center space-x-2 shadow-lg shadow-red-500/25 transition cursor-pointer shrink-0";
        if (headerPill && headerStatus) {
            headerPill.className = "hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-accent-950/40 border border-accent-800/60 text-accent-300";
            headerStatus.innerText = "Đang xử lý...";
        }
    } else {
        btnStart.disabled = false;
        btnStart.className = "flex-1 py-4 px-6 rounded-2xl bg-gradient-to-r from-brand-600 via-accent-600 to-accent-500 hover:from-brand-500 hover:to-accent-400 text-white font-extrabold text-sm shadow-xl shadow-brand-500/20 flex items-center justify-center space-x-2.5 transition-all duration-200 active:scale-[0.98]";
        btnAbort.disabled = true;
        btnAbort.className = "py-4 px-6 rounded-2xl bg-slate-800 text-slate-500 font-bold text-sm flex items-center justify-center space-x-2 transition cursor-not-allowed shrink-0";
        if (headerPill && headerStatus) {
            headerPill.className = "hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-emerald-950/40 border border-emerald-800/60 text-emerald-300";
            headerStatus.innerText = "Sẵn sàng";
        }
    }
}

function onTaskComplete(res) {
    setProcessingState(false);
    document.getElementById("main-progress-bar").style.width = "100%";
    document.getElementById("progress-percent-badge").innerText = "100%";

    const banner = document.getElementById("status-banner");
    banner.className = "mt-4 p-3.5 rounded-xl bg-brand-950/40 border border-brand-900/60 text-xs text-brand-300 flex items-center space-x-2.5";
    document.getElementById("status-banner-text").innerText = `🎉 Xử lý hoàn tất trong ${res.duration_seconds}s!`;

    outputFileName = res.output_filename;

    // Show Player Tab Selector
    const tabGroup = document.getElementById("player-tab-group");
    if (tabGroup) tabGroup.classList.remove("hidden");

    // Video player
    switchPlayerTab("output");

    // Download button
    const downloadBtn = document.getElementById("btn-download-video");
    const downloadUrl = `/api/video/download/${encodeURIComponent(res.output_filename)}?type=output`;
    downloadBtn.href = downloadUrl;
    downloadBtn.classList.remove("hidden");
    downloadBtn.classList.add("flex");

    // Comparison Matrix
    const compCard = document.getElementById("comparison-card");
    if (res.input_meta && res.output_meta) {
        document.getElementById("cmp-before").innerText = `${res.input_meta.resolution} • ${res.input_meta.fps} • ${res.input_meta.size_mb} MB`;
        document.getElementById("cmp-after").innerText = `${res.output_meta.resolution} • ${res.output_meta.fps} • ${res.output_meta.size_mb} MB`;
        compCard.classList.remove("hidden");
    }

    lucide.createIcons();
}

function switchPlayerTab(tab) {
    currentPlayerTab = tab;
    const player = document.getElementById("result-video-player");
    const placeholder = document.getElementById("video-placeholder");
    const tabOutput = document.getElementById("tab-player-output");
    const tabInput = document.getElementById("tab-player-input");

    if (tab === "output" && outputFileName) {
        tabOutput.className = "px-2.5 py-1 rounded-md bg-brand-600 text-white transition";
        tabInput.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-white transition";
        player.src = `/api/video/stream/${encodeURIComponent(outputFileName)}?type=output`;
    } else if (tab === "input" && selectedFileName) {
        tabInput.className = "px-2.5 py-1 rounded-md bg-accent-600 text-white transition";
        tabOutput.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-white transition";
        player.src = `/api/video/stream/${encodeURIComponent(selectedFileName)}?type=input`;
    }

    player.classList.remove("hidden");
    placeholder.classList.add("hidden");
    player.play().catch(() => {});
}

// ==========================================
// 6. PHÍM TẮT & MODALS
// ==========================================
function setupKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
        // Ctrl + Enter để Bắt đầu
        if (e.ctrlKey && e.key === "Enter") {
            e.preventDefault();
            const btnStart = document.getElementById("btn-start");
            if (btnStart && !btnStart.disabled) {
                startProcessing();
            }
        }
        // Esc để đóng modal hoặc abort
        if (e.key === "Escape") {
            closeSystemModal();
            closeHelpModal();
        }
    });
}

function openSystemModal() {
    fetchGpuStatus();
    document.getElementById("system-modal").classList.remove("hidden");
    lucide.createIcons();
}

function closeSystemModal() {
    document.getElementById("system-modal").classList.add("hidden");
}

function openHelpModal() {
    document.getElementById("help-modal").classList.remove("hidden");
    lucide.createIcons();
}

function closeHelpModal() {
    document.getElementById("help-modal").classList.add("hidden");
}
