import React from 'react';

// Icon component for visual elements
const Icon = ({ name, className }) => {
    const icons = {
        bot: <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2a2 2 0 0 0-2 2v2H8a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h1l-1.17 3.5a1.018 1.018 0 0 0 .97 1.5h4.4a1.018 1.018 0 0 0 .97-1.5L15 15h1a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-2V4a2 2 0 0 0-2-2m-3 8.5a1.5 1.5 0 1 1 0 3a1.5 1.5 0 0 1 0-3m6 0a1.5 1.5 0 1 1 0 3a1.5 1.5 0 0 1 0-3"/></svg>,
        lookup: <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="m15.5 14l-1.45-1.45l-.7-.7l-1.1-1.1l-2.8-2.8L5 3.5L3.5 5l5.05 5.05l-3.7 3.7l-1.1 1.1l-1.4 1.4L1 17.5l1.45 1.45l.7.7l1.1 1.1l3.5 3.5l1.45 1.45l1.45-1.45l3.7-3.7l1.1-1.1l1.4-1.4l1.4-1.4zm-2.85 2.85l-3.5-3.5l.7-.7l3.5 3.5zM10 20.5L8.5 19l5.05-5.05l1.5 1.5zm6.1-6.1l-3.5-3.5l.7-.7l3.5 3.5zM22 3.5L18.5 0l-5.15 5.15l3.5 3.5z"/></svg>,
        transform: <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M6.1 20.25q-.65 0-1.075-.425T4.6 18.75V5.8q0-.35.25-.6t.6-.25h.35L12 2l6.2 3l.35.05q.35.05.6.3t.25.6V18.75q0 .65-.425 1.075t-1.075.425zm0-1.5h11.8V6.35l-.3-.05L12 3.4l-5.5 2.85l-.3.05zM12 12.5l-2.1-2.1l1.05-1.05L12 10.4l3.15-3.15l1.05 1.05zm0 6.25l-2.1-2.1l1.05-1.05L12 16.65l3.15-3.15l1.05 1.05zM6.1 6.35V18.75z"/></svg>,
        user: <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4s-4 1.79-4 4s1.79 4 4 4m0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4"/></svg>,
        check: <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19L21 7l-1.41-1.41z"/></svg>,
        close: <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12z"/></svg>,
    };
    return <span className={className}>{icons[name]}</span>;
};

export default Icon;
