APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
    --edinburgh-navy:   #1a2744;
    --edinburgh-gold:   #c9a84c;
    --edinburgh-stone:  #f4f0e8;
    --edinburgh-slate:  #4a5568;
    --edinburgh-green:  #2d6a4f;
    --edinburgh-red:    #9b2335;
    --radius:           12px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--edinburgh-stone);
    color: var(--edinburgh-navy);
}

.block-container { padding: 1.5rem 2rem 2rem 2rem; max-width: 1400px; }
h1, h2, h3 { font-family: 'DM Serif Display', serif; }
</style>
"""