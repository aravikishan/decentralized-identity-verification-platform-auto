document.getElementById('verifyForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const userId = document.getElementById('userId').value;
    const response = await fetch(`/api/verify/${userId}`);
    const result = await response.json();
    alert('Verification status: ' + result.status);
});
