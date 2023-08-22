app.get('/', (req, res) => {
    res.send('Hello, World!');
});

// create a route that handles all paths that start with "posts/*"
