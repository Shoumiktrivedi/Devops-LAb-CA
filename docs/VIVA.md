# Viva Questions and Answers

1. **Why Flask?** It is lightweight and easy to learn, and gives full control over structure. For a small REST API it avoids the extra weight of Django.
2. **Why SQLite?** It needs no separate server, stores everything in one file, and is perfect for a single-user local project. For many users I would move to PostgreSQL.
3. **Why Docker?** It packages the app with all its dependencies, so it runs the same on any machine. It removes "works on my machine" problems.
4. **What is containerization?** Packaging an application and its dependencies into an isolated unit that shares the host OS kernel, so it is lighter than a virtual machine.
5. **Docker image vs container?** An image is a read-only template built from the Dockerfile. A container is a running instance of that image.
6. **What is Docker Compose?** A tool to define and run applications using a YAML file. One command, `docker compose up`, builds and starts everything.
7. **What is CI/CD?** Continuous Integration automatically builds and tests code on every change. Continuous Delivery/Deployment automatically releases it.
8. **Why GitHub Actions?** It is built into GitHub, needs no extra server, is free for public repos, and reacts to pushes and pull requests.
9. **What is a REST API?** An interface where resources have URLs and standard HTTP methods act on them, usually exchanging JSON, and each request is stateless.
10. **HTTP methods used?** GET to read, POST to create, PUT to update, DELETE to remove.
11. **GET vs POST vs PUT vs DELETE?** GET reads without changing data. POST creates a new resource. PUT replaces or updates an existing one. DELETE removes it.
12. **Which status codes do you use?** 200 OK, 201 Created, 400 Bad Request for validation errors, 404 Not Found, and 500 for server or database errors.
13. **What is SQLAlchemy?** A Python ORM. I define tables as classes and query with Python instead of raw SQL, which is also safer against SQL injection.
14. **What is CRUD?** Create, Read, Update, Delete — the four basic data operations. My app has all four for transactions.
15. **What is PyTest?** A Python testing framework with simple `assert` statements and fixtures. I use it to test all API endpoints.
16. **What is unit testing?** Testing a small piece of code, such as one function, in isolation.
17. **What is API testing?** Sending requests to endpoints and checking status codes and responses. Flask's test client does this without starting a real server.
18. **What is Git?** A distributed version control system that tracks changes and lets you go back or work in branches.
19. **What is GitHub?** A hosting platform for Git repositories that adds collaboration, pull requests and GitHub Actions.
20. **What is a Docker volume?** Storage managed by Docker outside the container's filesystem. My SQLite file lives in a volume, so data survives container restarts and rebuilds.
21. **What is `.dockerignore`?** It lists files Docker should not copy into the image, like `.git`, caches and local databases. This keeps the image small and clean.
22. **What is `requirements.txt`?** A list of Python packages with versions. `pip install -r requirements.txt` recreates the same environment.
23. **Why environment variables?** To keep configuration and secrets like `SECRET_KEY` and `DATABASE_URL` out of the code, so they can change per environment.
24. **Benefits of automation?** Faster feedback, fewer human mistakes, consistent builds, and bugs caught before they reach the main branch.
25. **Why a separate services layer?** Routes handle HTTP only; services hold validation and logic. It keeps code organized and easier to test.
26. **How do you prevent invalid data?** Client-side checks for quick feedback and server-side validation as the real protection: positive amount, valid date, category must match the type.
27. **What happens when you push to GitHub?** GitHub Actions starts, installs dependencies, runs PyTest, then builds the Docker image and checks the container health. A failing test stops the pipeline.
28. **Why gunicorn in Docker?** Flask's built-in server is for development. Gunicorn is a production-grade WSGI server.
29. **What is an application factory?** A `create_app()` function that builds the app with a given config. Tests use it to create an app with a separate test database.
30. **Future improvements?** Login and multiple users, PostgreSQL, budgets and alerts, exports, recurring transactions and cloud deployment.
