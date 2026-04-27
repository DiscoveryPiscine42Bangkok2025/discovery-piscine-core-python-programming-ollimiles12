// gameController.js — syncs the frontend board with Flask backend

const resultDiv = document.getElementById("result");
const boardInput = document.getElementById("boardInput");
const colorToggleBtn = document.getElementById("colorToggleBtn");

let currentBoardStr =
    "rnbqkbnr\n" +
    "pppppppp\n" +
    "........\n" +
    "........\n" +
    "........\n" +
    "........\n" +
    "PPPPPPPP\n" +
    "RNBQKBNR";

let currentTurn = 'w';
let enPassantTarget = null;   // { r, c } or null
let castlingRights = { wk: true, wq: true, bk: true, bq: true };

// 'white' or 'black' — which color pieces to place in puzzle mode
let addPieceColor = 'white';

const pieceToChar = {
    'king': 'k', 'queen': 'q', 'rook': 'r', 'bishop': 'b', 'knight': 'n', 'pawn': 'p'
};
const charToPiece = {
    'k': 'king', 'q': 'queen', 'r': 'rook', 'b': 'bishop', 'n': 'knight', 'p': 'pawn'
};

function renderBoardFromText(boardStr) {
    currentBoardStr = boardStr;
    boardInput.value = boardStr;
    const lines = boardStr.split('\n');

    const turnLabel = currentTurn === 'w' ? 'White' : 'Black';
    document.querySelector('.header p').textContent =
        `Setup a puzzle or Play! Current turn: ${turnLabel}`;

    for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
            const sq = document.getElementById(`${r}-${c}`);
            sq.innerHTML = '';
            sq.className = `square ${(r + c) % 2 === 0 ? 'white' : 'black'}`;

            const char = lines[r][c];
            if (char !== '.') {
                const isWhite = char === char.toUpperCase();
                const pieceName = charToPiece[char.toLowerCase()];

                const pieceDiv = document.createElement('div');
                pieceDiv.className = `piece ${pieceName} ${isWhite ? 'white-piece' : 'black-piece'}`;
                pieceDiv.draggable = true;

                pieceDiv.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('source-r', r);
                    e.dataTransfer.setData('source-c', c);
                });

                sq.appendChild(pieceDiv);
            }
        }
    }
}

// Set up drop zones
document.querySelectorAll('.board .square').forEach(sq => {
    sq.addEventListener('dragover', e => e.preventDefault());

    sq.addEventListener('drop', async (e) => {
        e.preventDefault();
        const sr = e.dataTransfer.getData('source-r');
        const sc = e.dataTransfer.getData('source-c');
        const dr = parseInt(sq.getAttribute('data-r'));
        const dc = parseInt(sq.getAttribute('data-c'));

        if (sr === '' || sc === '') return;

        const response = await fetch('/api/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                board: currentBoardStr,
                from: { r: parseInt(sr), c: parseInt(sc) },
                to: { r: dr, c: dc },
                turn: currentTurn,
                en_passant_target: enPassantTarget,
                castling_rights: castlingRights
            })
        });

        const data = await response.json();

        if (!data.valid) {
            resultDiv.textContent = `❌ Invalid Move: ${data.message}`;
            resultDiv.className = "result fail";
        } else {
            // Update state from server response
            currentTurn = data.turn;
            enPassantTarget = data.en_passant_target || null;
            castlingRights = data.castling_rights || castlingRights;

            // Show game status
            const status = data.status;
            if (status === 'checkmate') {
                const winner = currentTurn === 'w' ? 'Black' : 'White';
                resultDiv.textContent = `🏆 Checkmate! ${winner} wins!`;
                resultDiv.className = "result success";
            } else if (status === 'stalemate') {
                resultDiv.textContent = `🤝 Stalemate! It's a draw.`;
                resultDiv.className = "result loading";
            } else if (status === 'check') {
                resultDiv.textContent = `⚠️ Check! ${currentTurn === 'w' ? 'White' : 'Black'} is in check.`;
                resultDiv.className = "result loading";
                if (botEnabled && currentTurn === botColor) {
                    setTimeout(triggerBotMove, 100);
                }
            } else if (status === 'draw') {
                resultDiv.textContent = `🤝 Draw!`;
                resultDiv.className = "result loading";
            } else {
                resultDiv.textContent = `✅ Move played. ${currentTurn === 'w' ? "White" : "Black"}'s turn.`;
                resultDiv.className = "result success";
                if (botEnabled && currentTurn === botColor) {
                    setTimeout(triggerBotMove, 100);
                }
            }
        }

        renderBoardFromText(data.board);
    });
});

window.addEventListener("DOMContentLoaded", () => renderBoardFromText(currentBoardStr));

// --- Bot Logic ---
let botEnabled = false;
let botColor = 'b'; // Assume bot plays black by default

const botToggleBtn = document.getElementById("botToggleBtn");
const eloSelect = document.getElementById("eloSelect");

if (botToggleBtn) {
    botToggleBtn.addEventListener("click", () => {
        botEnabled = !botEnabled;
        botToggleBtn.textContent = `Bot: ${botEnabled ? "ON ✅" : "OFF"}`;
        botToggleBtn.classList.toggle("active", botEnabled);
        
        if (botEnabled && currentTurn === botColor) {
            triggerBotMove();
        }
    });
}

async function triggerBotMove() {
    if (!botEnabled || currentTurn !== botColor) return;
    
    resultDiv.textContent = "Bot is thinking...";
    resultDiv.className = "result loading";
    
    try {
        const elo = parseInt(eloSelect.value) || 1500;
        const res = await fetch('/api/bot_move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                board: currentBoardStr,
                turn: currentTurn,
                en_passant_target: enPassantTarget,
                castling_rights: castlingRights,
                elo: elo
            })
        });
        
        const data = await res.json();
        if (data.from && data.to) {
            const moveRes = await fetch('/api/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    board: currentBoardStr,
                    from: data.from,
                    to: data.to,
                    turn: currentTurn,
                    en_passant_target: enPassantTarget,
                    castling_rights: castlingRights,
                    promotion: data.promotion
                })
            });
            const moveData = await moveRes.json();
            
            if (moveData.valid) {
                currentTurn = moveData.turn;
                enPassantTarget = moveData.en_passant_target || null;
                castlingRights = moveData.castling_rights || castlingRights;
                
                const status = moveData.status;
                if (status === 'checkmate') {
                    resultDiv.textContent = `🏆 Checkmate! ${currentTurn === 'w' ? 'Black' : 'White'} wins!`;
                    resultDiv.className = "result success";
                } else if (status === 'stalemate' || status === 'draw') {
                    resultDiv.textContent = `🤝 Draw!`;
                    resultDiv.className = "result loading";
                } else {
                    resultDiv.textContent = `✅ Bot moved. ${currentTurn === 'w' ? "White" : "Black"}'s turn.`;
                    resultDiv.className = "result success";
                }
                
                renderBoardFromText(moveData.board);
            }
        } else {
            throw new Error(data.error || "No move returned");
        }
    } catch (e) {
        console.error(e);
        resultDiv.textContent = "Bot error!";
        resultDiv.className = "result fail";
    }
}


// --- Piece Placement (Puzzle Mode) ---
const addBtns = document.querySelectorAll('.addBtn');
const clearBtn = document.getElementById('clearBtn');
let pieceToAdd = null;

// Toggle white/black piece color when placing
if (colorToggleBtn) {
    colorToggleBtn.addEventListener('click', () => {
        addPieceColor = addPieceColor === 'white' ? 'black' : 'white';
        colorToggleBtn.textContent = `Placing: ${addPieceColor === 'white' ? '⬜ White' : '⬛ Black'}`;
    });
}

addBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        pieceToAdd = btn.getAttribute('data-piece');
        resultDiv.textContent = `Click a square to place a ${addPieceColor} ${pieceToAdd}`;
        resultDiv.className = "result loading";
    });
});

document.querySelectorAll('.board .square').forEach(sq => {
    sq.addEventListener('click', () => {
        if (pieceToAdd) {
            const r = parseInt(sq.getAttribute('data-r'));
            const c = parseInt(sq.getAttribute('data-c'));
            const lines = currentBoardStr.split('\n');
            let chars = lines[r].split('');

            // White pieces are uppercase, black pieces are lowercase
            const charBase = pieceToChar[pieceToAdd];
            chars[c] = addPieceColor === 'white' ? charBase.toUpperCase() : charBase;

            lines[r] = chars.join('');
            pieceToAdd = null;
            resultDiv.textContent = "Ready";
            resultDiv.className = "result";
            renderBoardFromText(lines.join('\n'));
        }
    });
});

// --- Timer Logic (driven by Flask /api/timer/* — timer.py on the server) ---

const clockDiv = document.getElementById("digital-clock");
const timeBtn  = document.getElementById("timeBtn");

let pollInterval = null;

function updateClockUI(state) {
    if (!clockDiv) return;
    const p1Active = state.running && state.turn === 1;
    const p2Active = state.running && state.turn === 2;
    clockDiv.innerHTML =
        `<span style="color:${p1Active ? '#4caf50' : '#fff'};font-weight:${p1Active ? 'bold' : 'normal'}">⬜ ${state.p1}</span>` +
        ` &nbsp;|&nbsp; ` +
        `<span style="color:${p2Active ? '#4caf50' : '#aaa'};font-weight:${p2Active ? 'bold' : 'normal'}">⬛ ${state.p2}</span>`;

    if (timeBtn) {
        timeBtn.textContent = state.running ? "⏸ Pause" : "▶ Start Timer";
    }

    if (state.timeout) {
        const winner = state.timeout === 1 ? "Black" : "White";
        resultDiv.textContent = `⏱️ ${winner} wins on time!`;
        resultDiv.className = "result success";
        stopPolling();
    }
}

async function fetchTimerState() {
    try {
        const res = await fetch('/api/timer/state');
        const state = await res.json();
        updateClockUI(state);
    } catch (e) { console.error("Timer poll failed", e); }
}

function startPolling() {
    if (pollInterval) return;
    pollInterval = setInterval(fetchTimerState, 800);
}

function stopPolling() {
    clearInterval(pollInterval);
    pollInterval = null;
}

if (timeBtn) {
    timeBtn.addEventListener("click", async () => {
        const stateRes = await fetch('/api/timer/state');
        const state = await stateRes.json();

        if (state.running) {
            await fetch('/api/timer/stop', { method: 'POST' });
            stopPolling();
        } else {
            await fetch('/api/timer/start', { method: 'POST' });
            startPolling();
        }
        fetchTimerState();
    });
}

// Init: fetch state on load so clock shows correct values
fetchTimerState();

clearBtn.addEventListener('click', async () => {
    enPassantTarget = null;
    castlingRights = { wk: true, wq: true, bk: true, bq: true };
    renderBoardFromText(
        "........\n" +
        "........\n" +
        "........\n" +
        "........\n" +
        "........\n" +
        "........\n" +
        "........\n" +
        "........"
    );
    // Reset the server clock too
    await fetch('/api/timer/reset', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({p1:600,p2:600}) });
    stopPolling();
    fetchTimerState();
});

// --- Reset to starting position ---
const resetBtn = document.getElementById("resetBtn");
if (resetBtn) {
    resetBtn.addEventListener('click', async () => {
        currentTurn = 'w';
        enPassantTarget = null;
        castlingRights = { wk: true, wq: true, bk: true, bq: true };
        renderBoardFromText(
            "rnbqkbnr\n" +
            "pppppppp\n" +
            "........\n" +
            "........\n" +
            "........\n" +
            "........\n" +
            "PPPPPPPP\n" +
            "RNBQKBNR"
        );
        resultDiv.textContent = "Ready";
        resultDiv.className = "result";
        await fetch('/api/timer/reset', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({p1:600,p2:600}) });
        stopPolling();
        fetchTimerState();
    });
}