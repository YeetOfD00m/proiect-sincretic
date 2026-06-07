// Simple IoT Control Panel

function updateStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('temperature').textContent = data.temperature ? data.temperature.toFixed(1) : '--';
            
            if (data.led_status) {
                document.getElementById('led-status').textContent = 'ON';
            } else {
                document.getElementById('led-status').textContent = 'OFF';
            }
            
            updateMessages(data.messages);
            updateFloodEvents(data.flood_events);
        })
        .catch(error => console.log('Error:', error));
}

function updateMessages(messages) {
    const container = document.getElementById('messages-list');
    
    if (!messages || messages.length === 0) {
        container.innerHTML = '<p>No messages</p>';
        return;
    }
    
    let html = '';
    messages.forEach(msg => {
        html += '<div class="list-item">' + msg.timestamp + ' - ' + msg.message + '</div>';
    });
    
    container.innerHTML = html;
}

function updateFloodEvents(events) {
    const container = document.getElementById('flood-events-list');
    
    if (!events || events.length === 0) {
        container.innerHTML = '<p>No events</p>';
        return;
    }
    
    let html = '';
    events.forEach((event, index) => {
        html += '<div class="list-item">' + event.timestamp + ' - ' + event.message + 
                ' <button onclick="deleteFloodEvent(' + index + ')" style="float:right;">Delete</button></div>';
    });
    
    container.innerHTML = html;
}

function turnLedOn() {
    fetch('/api/led/on', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('LED turned ON');
                updateStatus();
            }
        });
}

function turnLedOff() {
    fetch('/api/led/off', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('LED turned OFF');
                updateStatus();
            }
        });
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const msg = input.value;
    
    if (!msg) {
        alert('Please enter a message');
        return;
    }
    
    fetch('/api/message/send', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: msg})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Message sent');
            input.value = '';
            updateStatus();
        }
    });
}

function deleteFloodEvent(index) {
    fetch('/api/flood/delete/' + index, {method: 'DELETE'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatus();
            }
        });
}

function clearFloodEvents() {
    if (confirm('Clear all flood events?')) {
        fetch('/api/flood/clear', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateStatus();
                }
            });
    }
}

function clearMessages() {
    if (confirm('Clear all messages?')) {
        fetch('/api/messages/clear', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateStatus();
                }
            });
    }
}

setInterval(updateStatus, 2000);

document.addEventListener('DOMContentLoaded', function() {
    updateStatus();
});
