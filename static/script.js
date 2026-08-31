
const roomId = new URLSearchParams(location.search).get("room");

let myMemberId = null;
let currentRoundId = null;
let members = {};
let timerRunning = false;
let timerStart = 0;
let currentTime = 0;
let timerInterval = null;
let solveSubmitted = false;

const $ = id => document.getElementById(id);

const roomEntry = $("roomEntry");
const roomView = $("roomView");
const roomIdElement = $("roomId");
const playerNicknameElement = $("playerNickname");
const roundNumberElement = $("roundNumber");
const scrambleElement = $("scramble");
const connectionStatusElement = $("connectionStatus");
const resultsElement = $("results");
const timerElement = $("timer");
const penaltyInput = $("penalty");
const submitSolveButton = $("submitSolve");

const createEventInput = $("createEvent");
const createNicknameInput = $("createNickname");
const createColorInput = $("createColor");
const createRoomButton = $("createRoom");

const joinRoomIdInput = $("joinRoomId");
const joinNicknameInput = $("joinNickname");
const joinColorInput = $("joinColor");
const joinRoomButton = $("joinRoom");

function getStoredMemberId(room) {
    return localStorage.getItem(`cubeRaceMember:${room}`);
}

function setStoredMemberId(room, memberId) {
    localStorage.setItem(`cubeRaceMember:${room}`, memberId);
}

async function createRoom() {
    const event = createEventInput.value.trim();
    const nickname = createNicknameInput.value.trim();

    if (!event || !nickname) {
        alert("Enter event and nickname.");
        return;
    }

    try {
        const response = await fetch("/rooms", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                event,
                nickname,
                color: createColorInput.value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail ?? "Failed to create room.");
            return;
        }

        setStoredMemberId(data.room_id, data.member_id);
        location.href = `/?room=${data.room_id}`;
    } catch (error) {
        console.error(error);
        alert("Failed to create room.");
    }
}

async function joinRoom() {
    const targetRoomId = joinRoomIdInput.value.trim();
    const nickname = joinNicknameInput.value.trim();

    if (!targetRoomId || !nickname) {
        alert("Enter room ID and nickname.");
        return;
    }

    try {
        const response = await fetch(`/rooms/${targetRoomId}/join`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                nickname,
                color: joinColorInput.value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail ?? "Failed to join room.");
            return;
        }

        setStoredMemberId(targetRoomId, data.member_id);
        location.href = `/?room=${targetRoomId}`;
    } catch (error) {
        console.error(error);
        alert("Failed to join room.");
    }
}

async function loadRoom() {
    if (!roomId) return false;

    try {
        const response = await fetch(`/rooms/${roomId}`);

        if (!response.ok) {
            alert("Room not found.");
            return false;
        }

        const room = await response.json();

        members = {};
        resultsElement.innerHTML = "";

        for (const member of room.members) {
            members[member.id] = member;

            const row = document.createElement("tr");

            row.id = `member-${member.id}`;

            row.innerHTML = `
                <td>${escapeHtml(member.nickname)}</td>
                <td id="time-${member.id}">-</td>
            `;

            resultsElement.appendChild(row);
        }

        myMemberId = getStoredMemberId(roomId);

        if (myMemberId && members[myMemberId]) {
            playerNicknameElement.textContent =
                members[myMemberId].nickname;
        } else {
            playerNicknameElement.textContent = "Unknown";
        }

        return true;
    } catch (error) {
        console.error("Failed to load room:", error);
        return false;
    }
}

async function loadCurrentRound() {
    if (!roomId) return false;

    try {
        const response = await fetch(
            `/rooms/${roomId}/rounds/current`
        );

        if (!response.ok) {
            currentRoundId = null;
            roundNumberElement.textContent = "-";
            scrambleElement.textContent = "Waiting for round...";
            return false;
        }

        const round = await response.json();
        setRound(round);

        return true;
    } catch (error) {
        console.error("Failed to load current round:", error);
        return false;
    }
}

async function loadCurrentSolves() {
    if (!roomId || !currentRoundId) return;

    try {
        const response = await fetch(
            `/rooms/${roomId}/rounds/${currentRoundId}/solves`
        );

        if (!response.ok) return;

        const solves = await response.json();

        clearResults();

        for (const solve of solves) {
            updateSolve({
                member_id: solve.member_id,
                time: solve.time,
                penalty: solve.penalty
            });
        }
    } catch (error) {
        console.error("Failed to load solves:", error);
    }
}

async function loadStats() {
    if (!roomId) return;

    try {
        const response = await fetch(
            `/rooms/${roomId}/stats`
        );

        if (!response.ok) {
            console.warn(
                "Stats endpoint unavailable."
            );
            return;
        }

        const stats = await response.json();

        renderStats(stats);
    } catch (error) {
        console.error("Failed to load stats:", error);
    }
}

function renderStats(stats) {
    if (stats.records) {
        $("bestSingle").textContent =
            formatStat(stats.records.single);

        $("bestAo5").textContent =
            formatStat(stats.records.ao5);

        $("bestAo12").textContent =
            formatStat(stats.records.ao12);

        $("bestAo25").textContent =
            formatStat(stats.records.ao25);

        $("bestAo50").textContent =
            formatStat(stats.records.ao50);

        $("bestAo100").textContent =
            formatStat(stats.records.ao100);
    }

    renderPlayers(stats.players ?? []);
    renderHistory(stats.history ?? []);
}

function renderPlayers(players) {
    const container = $("playerStats");

    container.innerHTML = "";

    if (!players.length) {
        container.innerHTML =
            `<div class="empty-state">No players.</div>`;

        return;
    }

    for (const player of players) {
        const card = document.createElement("div");

        card.className = "player-card";

        card.innerHTML = `
            <div class="player-name">
                ${escapeHtml(player.nickname)}
            </div>

            <div class="player-summary">
                <div class="player-stat">
                    <span>Wins</span>
                    <strong>${player.wins ?? 0}</strong>
                </div>

                <div class="player-stat">
                    <span>Median</span>
                    <strong>${formatStat(player.median)}</strong>
                </div>
            </div>
        `;

        container.appendChild(card);
    }
}

function renderHistory(history) {
    const container = $("history");

    container.innerHTML = "";

    if (!history.length) {
        container.innerHTML =
            `<div class="empty-state">No solves yet.</div>`;

        return;
    }

    for (const item of history) {
        const row = document.createElement("div");

        row.className = "history-item";

        row.innerHTML = `
            <span class="history-round">
                #${item.round}
            </span>

            <span class="history-player">
                ${escapeHtml(item.nickname)}
            </span>

            <strong class="history-result">
                ${escapeHtml(item.result)}
            </strong>
        `;

        container.appendChild(row);
    }
}

function formatStat(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    if (typeof value === "string") {
        return value;
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "-";
    }

    return number.toFixed(2);
}

function setRound(round) {
    console.log("SET ROUND:", round.id, round.number);
    currentRoundId = Number(round.id);
    roundNumberElement.textContent = round.number;
    scrambleElement.textContent = round.scramble;
    solveSubmitted = false;
    resetTimer();
    penaltyInput.value = "none";
    submitSolveButton.disabled = false;
    clearResults();
    loadCurrentSolves();
}

function connectWebSocket() {
    if (!roomId) return;

    const protocol =
        location.protocol === "https:" ? "wss:" : "ws:";

    const websocket = new WebSocket(
        `${protocol}//${location.host}/ws/rooms/${roomId}`
    );

    websocket.onopen = () => {
        connectionStatusElement.textContent =
            "Connected";

        connectionStatusElement.className =
            "connected";
    };

    websocket.onclose = () => {
        connectionStatusElement.textContent =
            "Disconnected";

        connectionStatusElement.className =
            "disconnected";
    };

    websocket.onerror = error => {
        console.error("WebSocket:", error);
    };

    websocket.onmessage = event => {
        try {
            const data = JSON.parse(event.data);

            console.log("WS:", data);

            handleWebSocketMessage(data);
        } catch (error) {
            console.error(
                "Invalid WebSocket message:",
                error
            );
        }
    };

    window.cubeRaceWebSocket = websocket;
}

function handleWebSocketMessage(data) {
    console.log("WS:", data);

    if (data.type === "solve_submitted") {
        updateSolve(data);
        loadStats();
        return;
    }

    if (data.type === "round_started") {
        console.log("Starting new round:", data.round_id);

        setRound({
            id: data.round_id,
            number: data.number,
            scramble: data.scramble
        });

        loadStats();
        return;
    }

    if (data.type === "round_completed") {
        console.log("Round completed:", data.round_id);

        loadStats();
        return;
    }

    if (data.type === "member_joined") {
        loadRoom();
        loadStats();
        return;
    }

    if (data.type === "member_left") {
        loadRoom();
        loadStats();
        return;
    }
}

function updateSolve(data) {
    const timeElement =
        $(`time-${data.member_id}`);

    if (!timeElement) {
        return;
    }

    timeElement.textContent =
        formatSolve(data.time, data.penalty);

    if (data.member_id === myMemberId) {
        solveSubmitted = true;
    }
}

async function submitSolve() {
    if (!roomId) {
        alert("No room.");
        return;
    }

    if (!currentRoundId) {
        alert("No active round.");
        return;
    }

    if (!myMemberId) {
        alert("You are not identified in this room.");
        return;
    }

    if (solveSubmitted) {
        alert("You already submitted a solve for this round.");
        return;
    }

    if (timerRunning) {
        alert("Stop the timer first.");
        return;
    }

    if (!Number.isFinite(currentTime) || currentTime <= 0) {
        alert("No solve time.");
        return;
    }

    const roundIdAtSubmit = currentRoundId;
    const timeAtSubmit = currentTime;
    const penalty = penaltyInput.value;

    submitSolveButton.disabled = true;

    try {
        const response = await fetch(
            `/rooms/${roomId}/rounds/${roundIdAtSubmit}/solves`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    member_id: myMemberId,
                    time: timeAtSubmit,
                    penalty: penalty
                })
            }
        );

        if (!response.ok) {
            let data = {};

            try {
                data = await response.json();
            } catch {}

            console.error("Submit HTTP error:", response.status, data);

            alert(
                data.detail ??
                `Failed to submit solve. HTTP ${response.status}`
            );

            return;
        }

        solveSubmitted = true;
        submitSolveButton.blur();
        console.log(
            "Solve submitted successfully:",
            roundIdAtSubmit,
            timeAtSubmit,
            penalty
        );

        await loadStats();

    } catch (error) {
        console.error("Submit request error:", error);
        alert("Failed to submit solve.");
    } finally {
        submitSolveButton.disabled = false;
    }
}

function formatSolve(time, penalty) {
    if (penalty === "DNF") {
        return "DNF";
    }

    const value = Number(time);

    if (!Number.isFinite(value)) {
        return "-";
    }

    if (penalty === "+2") {
        return `${(value + 2).toFixed(2)}+`;
    }

    return value.toFixed(2);
}

function clearResults() {
    for (const memberId of Object.keys(members)) {
        const element =
            $(`time-${memberId}`);

        if (element) {
            element.textContent = "-";
        }
    }
}

function resetTimer() {
    timerRunning = false;

    if (timerInterval !== null) {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    timerStart = 0;
    currentTime = 0;

    timerElement.textContent = "0.00";
}
function startTimer() {
    if (timerRunning) return;
    if (solveSubmitted) return;
    if (!currentRoundId) return;

    console.log("TIMER START - round:", currentRoundId);

    timerRunning = true;
    timerStart = performance.now();
    currentTime = 0;

    timerElement.textContent = "0.00";

    timerInterval = setInterval(() => {
        currentTime =
            (performance.now() - timerStart) / 1000;

        timerElement.textContent =
            currentTime.toFixed(2);
    }, 10);
}

function stopTimer() {
    if (!timerRunning) return;

    timerRunning = false;

    if (timerInterval !== null) {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    currentTime =
        (performance.now() - timerStart) / 1000;

    timerElement.textContent =
        currentTime.toFixed(2);

    console.log(
        "TIMER STOP:",
        currentTime,
        "round:",
        currentRoundId
    );
}
function handleKeyboard(event) {
    if (event.code !== "Space") {
        return;
    }

    const tag = document.activeElement?.tagName;

    if (
        tag === "INPUT" ||
        tag === "SELECT" ||
        tag === "TEXTAREA"
    ) {
        return;
    }

    event.preventDefault();

    if (timerRunning) {
        stopTimer();
        return;
    }

    if (solveSubmitted) {
        return;
    }

    if (!currentRoundId) {
        console.warn("SPACE ignored - no current round");
        return;
    }

    startTimer();
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

createRoomButton.addEventListener(
    "click",
    createRoom
);

joinRoomButton.addEventListener(
    "click",
    joinRoom
);

submitSolveButton.addEventListener(
    "click",
    submitSolve
);

document.addEventListener(
    "keydown",
    handleKeyboard
);

async function init() {
    if (!roomId) {
        roomEntry.classList.remove("d-none");
        roomView.classList.add("d-none");
        return;
    }

    roomEntry.classList.add("d-none");
    roomView.classList.remove("d-none");

    roomIdElement.textContent = roomId;

    const loaded = await loadRoom();

    if (!loaded) {
        roomEntry.classList.remove("d-none");
        roomView.classList.add("d-none");
        return;
    }

    await loadCurrentRound();
    await loadStats();

    connectWebSocket();
}

init();