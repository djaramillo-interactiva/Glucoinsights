function httpRequest(params) {
    let body = JSON.stringify(params.data);
    let files = false;

    let formData = new FormData();
    for (const key of Object.keys(params.data)) {
        formData.append(key, params.data[key]);
        if (params.data[key] instanceof File) {
            files = true;
        }
    }

    if (files) {
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        if (params.method.toLowerCase() === 'get') {
            throw new Error('No se pueden enviar archivos con metodo GET.');
        }
    }

    const options = {
        method: params.method,
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        referrerPolicy: 'same-origin',
        body: files ? formData : body
    }

    if (files) {
        delete options.headers;
    }

    const url = new URL(params.url, location.origin);
    if (params.method.toLowerCase() === 'get') {
        delete options.body;
        url.search = new URLSearchParams(params.data).toString();
    }
    return fetch(url, options);
}

function httpPromise(params) {
    return new Promise((resolve, reject) => {
        httpRequest(params).then((res) => {
            res.json().then((data) => {
                resolve(data)
            }).catch(() => {
                resolve(res);
            })
        }).catch((error) => {
            reject(error);
        })
    })
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function submitData(data, method, url) {
    if (!url) {
        url = location.pathname;
    }

    return httpRequest({method, data, url})
        .then(res => {
            if (res.status === 500) {
                res.blob().then(blob => {
                    window.open(URL.createObjectURL(blob));
                });
            } else if (res.status >= 400) {
                alert('Error en el formulario');
            } else {
                return res.json()
            }
        });
}
