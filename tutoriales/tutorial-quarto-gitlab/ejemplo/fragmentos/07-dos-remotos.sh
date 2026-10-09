# Publicar el mismo sitio en GitHub Pages y en GitLab Pages desde un solo repositorio.
git remote -v                                   # origin -> github-personal
git remote add gitlab git@gitlab-personal:<usuario-gitlab>/sitio-gitlab.git
git push -u gitlab main                         # primer envío a GitLab
git push origin main && git push gitlab main    # en adelante, a los dos
