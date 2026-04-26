// gameController.js — syncs the frontend board with Flask backend

const checkBtn = document.getElementById("checkBtn");
const bestMoveBtn = document.getElementById("bestMoveBtn");
const resultDiv = document.getElementById("result");
const boardInput = document.getElementById("boardInput");

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
    
    document.querySelector('.header p').textContent = `Setup a puzzle or Play! Current turn: ${currentTurn === 'w' ? 'White' : 'Black'}`;
    
    for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
            const sq = document.getElementById(`${r}-${c}`);
            sq.innerHTML = ''; // clear
            sq.className = `square ${(r+c)%2===0 ? 'white' : 'black'}`; // reset bg
            
            const char = lines[r][c];
            if (char !== '.') {
                const isWhite = char === char.toUpperCase();
                const pieceName = charToPiece[char.toLowerCase()];
                
                const pieceDiv = document.createElement('div');
                pieceDiv.className = `piece ${pieceName} ${isWhite ? 'white-piece' : 'black-piece'}`;
                pieceDiv.draggable = true;
                
                // Drag start
                pieceDiv.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('source-r', r);
                    e.dataTransfer.setData('source-c', c);
                });
                
                sq.appendChild(pieceDiv);
            }
        }
    }
}

// Initialize Board Drop zones
document.querySelectorAll('.board .square').forEach(sq => {
    sq.addEventListener('dragover', e => e.preventDefault());
    sq.addEventListener('drop', async (e) => {
        e.preventDefault();
        const sr = e.dataTransfer.getData('source-r');
        const sc = e.dataTransfer.getData('source-c');
        const dr = parseInt(sq.getAttribute('data-r'));
        const dc = parseInt(sq.getAttribute('data-c'));
        
        if (sr === '' || sc === '') return; // came from outside
        
        // Call backend to update state
        const response = await fetch('/api/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                board: currentBoardStr,
                from: { r: parseInt(sr), c: parseInt(sc) },
                to: { r: dr, c: dc },
                turn: currentTurn
            })
        });
        
        const data = await response.json();
        
        if (!data.valid) {
            resultDiv.textContent = `❌ Invalid Move: ${data.message}`;
            resultDiv.className = "result fail";
        } else {
            currentTurn = data.turn;
            resultDiv.textContent = "✅ Move played.";
            resultDiv.className = "result success";
        }
        
        renderBoardFromText(data.board);
    });
});

window.addEventListener("DOMContentLoaded", () => renderBoardFromText(currentBoardStr));

const addBtns = document.querySelectorAll('.addBtn');
const clearBtn = document.getElementById('clearBtn');
let pieceToAdd = null;

addBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        pieceToAdd = btn.getAttribute('data-piece');
        resultDiv.textContent = `Click a square to place a ${pieceToAdd}`;
    });
});

document.querySelectorAll('.board .square').forEach(sq => {
    sq.addEventListener('click', () => {
        if (pieceToAdd) {
            const r = parseInt(sq.getAttribute('data-r'));
            const c = parseInt(sq.getAttribute('data-c'));
            const lines = currentBoardStr.split('\n');
            let chars = lines[r].split('');
            // Upper case for puzzle standard
            chars[c] = pieceToChar[pieceToAdd].toUpperCase();
            lines[r] = chars.join('');
            
            pieceToAdd = null;
            resultDiv.textContent = "Ready";
            renderBoardFromText(lines.join('\n'));
        }
    });
});

clearBtn.addEventListener('click', () => {
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
});

checkBtn.addEventListener("click", async () => {
    resultDiv.textContent = "Checking...";
    resultDiv.className = "result loading";
    try {
        const response = await fetch("/api/checkmate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ board: currentBoardStr })
        });
        const data = await response.json();
        resultDiv.className = "result " + (data.checkmate ? "success" : "fail");
        resultDiv.textContent = data.checkmate
            ? `✅ Checkmate! (${data.message})`
            : `❌ Not checkmate. (${data.message})`;
    } catch (err) {
        resultDiv.className = "result fail";
        resultDiv.textContent = "Error: " + err.message;
    }
});

bestMoveBtn.addEventListener("click", async () => {
    resultDiv.textContent = "Finding best move...";
    resultDiv.className = "result loading";
    try {
        const response = await fetch("/api/best_move", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ board: currentBoardStr })
        });
        const data = await response.json();
        resultDiv.className = "result " + (data.result.includes("No move") ? "fail" : "success");
        resultDiv.textContent = data.result || "No result returned.";
    } catch (err) {
        resultDiv.className = "result fail";
        resultDiv.textContent = "Error: " + err.message;
    }
});