/**
 * Video2X Web UI Controller (Vanilla JavaScript)
 * Quản lý tương tác DOM, Upload file, SSE Live Progress & Logs, Video Stream.
 */

let selectedFilePath = "";
let currentTaskMode = "realesrgan";
let currentScale = 4;
let currentRifeMul = 2;
let sseEventSource = null;

// ==========================================
// 1. KHỞI TẠO VÀ LOAD TRẠNG THÁI HỆ THỐNG
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    fetchSystemEnvironment();
    fetchGpuStatus();
    connectSSE();
    setupDropzone();
});

async function fetchSystemEnvironment() {
    try {
        const res = await fetch("/api/system/env");
        if (res.ok) {
            const data = await res.json();
            const vulkanText = document.getElementById("vulkan-text");
            const badgeVulkan = document.getElementById("badge-vulkan");
            if (vulkanText) {
                if (data.vulkan) {
                    vulkanText.innerText = data.vulkan_device;
                    vulkanText.classList.remove("text-slate-300", "text-rose-400", "text-amber-400");
                    vulkanText.classList.add("text-emerald-400");
                } else {
                    vulkanText.innerText = data.vulkan_device ? `Vulkan: ${data.vulkan_device}` : "Vulkan Chưa sẵn sàng";
                    vulkanText.classList.remove("text-slate-300", "text-emerald-400");
                    vulkanText.classList.add("text-amber-400");
                }
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
            // Update modal fields
            const mName = document.getElementById("modal-gpu-name");
            const mDriver = document.getElementById("modal-gpu-driver");
            const mVram = document.getElementById("modal-gpu-vram");
            const mTemp = document.getElementById("modal-gpu-temp");
            const mRaw = document.getElementById("modal-nvidia-raw");

            if (mName) mName.innerText = data.name;
            if (mDriver) mDriver.innerText = data.driver_ver;
            if (mVram) mVram.innerText = `${data.vram_used} / ${data.vram_total}`;
            if (mTemp) mTemp.innerText = data.temperature;
            if (mRaw) mRaw.innerText = data.raw_output || "Không có thông tin.";
        }
    } catch (e) {
        console.error("Lỗi lấy thông tin GPU:", e);
    }
}

// ==========================================
// 2. QUẢN LÝ CHỌN / TẢI VIDEO
// ==========================================
function switchInputMode(mode) {
    const uploadBtn = document.getElementById("tab-btn-upload");
    const pathBtn = document.getElementById("tab-btn-path");
    const uploadSec = document.getElementById("input-section-upload");
    const pathSec = document.getElementById("input-section-path");

    if (mode === "upload") {
        uploadBtn.className = "px-2.5 py-1 rounded-md bg-accent-600 text-white transition";
        pathBtn.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-white transition";
        uploadSec.classList.remove("hidden");
        pathSec.classList.add("hidden");
    } else {
        pathBtn.className = "px-2.5 py-1 rounded-md bg-accent-600 text-white transition";
        uploadBtn.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-white transition";
        pathSec.classList.remove("hidden");
        uploadSec.classList.add("hidden");
    }
}

function setupDropzone() {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("video-file-input");

    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("border-accent-500", "bg-slate-900");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("border-accent-500", "bg-slate-900");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("border-accent-500", "bg-slate-900");
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
    const card = document.getElementById("video-meta-card");
    document.getElementById("meta-filename").innerText = meta.filename;
    document.getElementById("meta-res").innerText = meta.resolution;
    document.getElementById("meta-fps").innerText = meta.fps;
    document.getElementById("meta-dur").innerText = meta.duration;
    document.getElementById("meta-size").innerText = meta.size_mb + " MB";
    card.classList.remove("hidden");
    lucide.createIcons();
}

function clearSelectedVideo() {
    selectedFilePath = "";
    document.getElementById("video-meta-card").classList.add("hidden");
    document.getElementById("dataset-filepath-input").value = "";
    document.getElementById("video-file-input").value = "";
}

// ==========================================
// 3. ĐIỀU KHIỂN CHẾ ĐỘ & MÔ HÌNH AI
// ==========================================
function selectTaskMode(mode) {
    currentTaskMode = mode;
    const modes = ["realesrgan", "libplacebo", "rife"];

    modes.forEach((m) => {
        const btn = document.getElementById(`mode-btn-${m}`);
        const group = document.getElementById(`group-${m}`);
        if (m === mode) {
            btn.className = "py-2.5 rounded-lg bg-accent-600 text-white transition text-center flex flex-col items-center";
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
            b.className = "scale-btn py-1.5 rounded-lg border border-accent-500 bg-accent-600/20 text-xs font-semibold text-accent-400";
        } else {
            b.className = "scale-btn py-1.5 rounded-lg border border-slate-700 bg-slate-950 text-xs font-semibold text-slate-300 hover:border-accent-500";
        }
    });
}

function setRifeMul(val) {
    currentRifeMul = val;
    document.querySelectorAll(".rife-mul-btn").forEach((b) => {
        if (parseInt(b.dataset.mul) === val) {
            b.className = "rife-mul-btn py-2 rounded-lg border border-accent-500 bg-accent-600/20 text-xs font-semibold text-accent-400";
        } else {
            b.className = "rife-mul-btn py-2 rounded-lg border border-slate-700 bg-slate-950 text-xs font-semibold text-slate-300";
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
// 4. TIẾN TRÌNH & SERVER-SENT EVENTS (SSE)
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
            const err = JSON.parse(e.data);
            appendTerminalLog("❌ Lỗi: " + (err.message || "Tiến trình thất bại"));
            setProcessingState(false);
            const banner = document.getElementById("status-banner");
            banner.className = "mt-4 p-3 rounded-xl bg-red-950/40 border border-red-900/60 text-xs text-red-300 flex items-center space-x-2";
            document.getElementById("status-banner-text").innerText = err.message || "Lỗi xử lý";
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
    banner.className = "mt-4 p-3 rounded-xl bg-accent-950/40 border border-accent-900/60 text-xs text-accent-300 flex items-center space-x-2";
    document.getElementById("status-banner-text").innerText = p.status_text;
}

function appendTerminalLog(text) {
    const logsEl = document.getElementById("terminal-logs");
    const p = document.createElement("p");
    p.textContent = text;
    logsEl.appendChild(p);
    logsEl.scrollTop = logsEl.scrollHeight;
}

function clearLogs() {
    document.getElementById("terminal-logs").innerHTML = "";
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

    if (running) {
        btnStart.disabled = true;
        btnStart.className = "flex-1 py-3.5 px-6 rounded-xl bg-slate-800 text-slate-500 font-bold text-sm cursor-not-allowed flex items-center justify-center space-x-2";
        btnAbort.disabled = false;
        btnAbort.className = "py-3.5 px-5 rounded-xl bg-red-600 hover:bg-red-500 text-white font-semibold text-sm flex items-center justify-center space-x-2 shadow-lg shadow-red-500/20 transition cursor-pointer";
    } else {
        btnStart.disabled = false;
        btnStart.className = "flex-1 py-3.5 px-6 rounded-xl bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 text-white font-bold text-sm shadow-lg shadow-brand-500/25 flex items-center justify-center space-x-2 transition active:scale-[0.98]";
        btnAbort.disabled = true;
        btnAbort.className = "py-3.5 px-5 rounded-xl bg-slate-800 text-slate-500 font-semibold text-sm flex items-center justify-center space-x-2 transition cursor-not-allowed";
    }
}

function onTaskComplete(res) {
    setProcessingState(false);
    document.getElementById("main-progress-bar").style.width = "100%";
    document.getElementById("progress-percent-badge").innerText = "100%";

    const banner = document.getElementById("status-banner");
    banner.className = "mt-4 p-3 rounded-xl bg-brand-950/40 border border-brand-900/60 text-xs text-brand-300 flex items-center space-x-2";
    document.getElementById("status-banner-text").innerText = `🎉 Xử lý hoàn tất trong ${res.duration_seconds}s!`;

    // Video player
    const player = document.getElementById("result-video-player");
    const placeholder = document.getElementById("video-placeholder");
    const downloadBtn = document.getElementById("btn-download-video");

    const streamUrl = `/api/video/stream/${encodeURIComponent(res.output_filename)}?type=output`;
    const downloadUrl = `/api/video/download/${encodeURIComponent(res.output_filename)}?type=output`;

    player.src = streamUrl;
    player.classList.remove("hidden");
    placeholder.classList.add("hidden");

    downloadBtn.href = downloadUrl;
    downloadBtn.classList.remove("hidden");
    downloadBtn.classList.add("flex");

    // Comparison
    const compCard = document.getElementById("comparison-card");
    if (res.input_meta && res.output_meta) {
        document.getElementById("cmp-before").innerText = `${res.input_meta.resolution} • ${res.input_meta.fps} • ${res.input_meta.size_mb} MB`;
        document.getElementById("cmp-after").innerText = `${res.output_meta.resolution} • ${res.output_meta.fps} • ${res.output_meta.size_mb} MB`;
        compCard.classList.remove("hidden");
    }

    lucide.createIcons();
}

// ==========================================
// 5. MODAL QUẢN LÝ PHẦN CỨNG
// ==========================================
function openSystemModal() {
    fetchGpuStatus();
    document.getElementById("system-modal").classList.remove("hidden");
    lucide.createIcons();
}

function closeSystemModal() {
    document.getElementById("system-modal").classList.add("hidden");
}
