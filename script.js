const sessionId = crypto.randomUUID();
const apiUrl = 'http://localhost:8000/chat'; // Update if needed

async function sendToAI() {
  const question = document.getElementById('question').value.trim();
  const answer = document.getElementById('answer').value.trim();
  const responseBox = document.getElementById('ai-response');
  const difficultyBox = document.getElementById('difficulty');
  const loader = document.getElementById('loading');
  const historyList = document.getElementById('history-list');

  if (!question || !answer) {
    alert("Please enter both a question and an answer.");
    return;
  }

  loader.style.display = 'block';
  responseBox.style.display = 'none';
  difficultyBox.style.display = 'none';

  const payload = {
    session_id: sessionId,
    question,
    answer
  };

  try {
    const res = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    loader.style.display = 'none';

    // Show AI response
    responseBox.innerText = data.reply;
    responseBox.style.display = 'block';

    // Show difficulty
    if (data.difficulty) {
      difficultyBox.innerText = `Difficulty: ${data.difficulty}`;
      difficultyBox.className = `difficulty ${data.difficulty.toLowerCase()}`;
      difficultyBox.style.display = 'inline-block';
    }

    // Update history
    historyList.innerHTML = '';
    data.history.forEach(entry => {
      const div = document.createElement('div');
      div.classList.add('history-entry');
      div.innerHTML = `<strong>You:</strong> ${entry.user}<br/><strong>AI:</strong> ${entry.ai}`;
      historyList.appendChild(div);
    });

  } catch (error) {
    loader.style.display = 'none';
    alert('Error communicating with the server.');
    console.error(error);
  }
}
