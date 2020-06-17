// Initialise some variables
var fileInput = document.getElementById('file-input');
var fileCatcher = document.getElementById('files-and-config');
var progressBar = document.getElementById('progressbar');

var filesUploaded = 0;
var fileList = [];

// Add files
fileInput.addEventListener('change', function(event) {
    fileList = [];
    for (var i = 0; i < fileInput.files.length; i++) {
        fileList.push(fileInput.files[i]);
    }
    document.getElementById('file-label').textContent = fileList.length + ' files selected';
});

// Send files and submit when finished
fileCatcher.addEventListener('submit', function (event) {
    if (fileList.length > 0) {
        document.getElementById('progress_indicator').style.display = ''
    };
    event.preventDefault();
    sendFileArray(fileList, progressBar).then(function (result) {
        if (result === 'success') {
            fileCatcher.submit()
        };
    });
});

// Send all files in an array (should return a promise)
sendFileArray = function(fileArray, progressBar) {
    var counter = 0;
    return new Promise((resolve, reject) => {
        fileArray.forEach(function (file) {
            sendFile(file).then(function(result) {
                counter++;
                var progressUpdate = counter * 100 / fileArray.length;
                progressBar.style.width = progressUpdate + "%";
                progressBar.textContent = counter + "/" + fileArray.length + " uploaded";
            if (counter == fileArray.length) {
                progressBar.textContent = 'Success. Calculating...';
                resolve("success")};
            }).catch(function(result) {
                progressBar.style.width = "100%";
                progressBar.textContent = 'Problem - try again!';
                progressBar.className = "progress-bar progress-bar-striped progress-bar-animated bg-danger";
                var xhr = new XMLHttpRequest();
                xhr.open("POST", '/clear');
                xhr.send(new FormData());
                })
        });
    });
};

sendFile = function(file) {
    return new Promise((resolve, reject) => {
        var formData = new FormData();
        var xhr = new XMLHttpRequest();
        formData.set('file', file);
        xhr.open("POST", '/sendfile');
        xhr.send(formData);
        xhr.onload = function (e) {
            if (xhr.readyState === 4) {
                if (JSON.parse(xhr.response).status_code === 200) {
                    resolve(xhr.responseText);
                }
                else {
                    reject(xhr.statusText);
                }
            }
        };    
    });
};