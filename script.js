document.getElementById('humanize-btn').addEventListener('click', () => {
    const inputCode = document.getElementById('input-code').value;
    const namingConvention = document.getElementById('naming-convention').value;
    const addComments = document.getElementById('add-comments').checked;
    const convertLoops = document.getElementById('convert-loops').checked;
    const loader = document.getElementById('loader');

    // Show the loader
    loader.style.display = 'block';
    document.getElementById('output-code').value = '';

    fetch('/humanize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: inputCode,
            options: {
                naming_convention: namingConvention,
                add_comments: addComments,
                convert_loops: convertLoops
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('output-code').value = data.code;
    })
    .catch(error => {
        document.getElementById('output-code').value = 'Error: Failed to humanize code.';
        console.error('Error:', error);
    })
    .finally(() => {
        // Hide the loader
        loader.style.display = 'none';
    });
});
