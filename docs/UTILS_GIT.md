Resolver o problema do arquivo grande no Git:

```markdown
# Como Remover um Arquivo Grande do Histórico do Git e Fazer Push

Este guia explica como remover um arquivo grande do histórico do seu repositório Git, permitindo que você faça push para plataformas como o GitHub, que têm limites de tamanho de arquivo.

---

### Cenário

Você tentou fazer `git push` e recebeu um erro similar a este:

```
remote: error: File data/dbqueimadas_CSV.zip is 109.01 MB; this exceeds GitHub's file size limit of 100.00 MB
```

Isso significa que um arquivo grande foi commitado no seu histórico e precisa ser removido.

---

### Passo 1: Remover o arquivo do seu diretório local (se ainda estiver lá)

Certifique-se de que o arquivo grande não esteja mais no seu diretório de trabalho.

**No Windows (PowerShell):**

```bash
del data\dbqueimadas_CSV.zip
```

**No Linux/macOS:**

```bash
rm data/dbqueimadas_CSV.zip
```

Verifique o status do Git para confirmar que o arquivo não aparece mais:

```bash
git status
```

---

### Passo 2: Remover o arquivo do histórico de commits com `git filter-branch`

Este comando reescreverá o histórico da sua branch, removendo o arquivo grande de todos os commits.

**Atenção:** A reescrita do histórico é uma operação poderosa. Certifique-se de estar na branch correta (`motoshima` no seu caso) e de que entende as implicações.

```bash
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch data/dbqueimadas_CSV.zip" --prune-empty --tag-name-filter cat -- --all
```

**Explicação:**
- `--force`: Permite a reescrita do histórico.
- `--index-filter "..."`: Executa um comando em cada commit.
- `git rm --cached --ignore-unmatch data/dbqueimadas_CSV.zip`: Remove o arquivo `data/dbqueimadas_CSV.zip` do índice (histórico) de cada commit. `--ignore-unmatch` evita erros se o arquivo não existir em um commit específico.
- `--prune-empty`: Remove commits que se tornarem vazios após a remoção do arquivo.
- `--tag-name-filter cat`: Garante que as tags sejam reescritas corretamente.
- `-- --all`: Aplica a operação a todas as branches e tags.

---

### Passo 3: Limpar referências antigas do Git

Após reescrever o histórico, o Git mantém referências antigas. É importante limpá-las.

```bash
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**Explicação:**
- Os dois primeiros comandos removem as referências (`refs/original`) que o `filter-branch` cria.
- `git gc --prune=now --aggressive`: Limpa objetos inacessíveis e otimiza o repositório.

---

### Passo 4: Forçar o push da branch reescrita

Como o histórico foi alterado, um `git push` normal falhará. Você precisa forçar o push. Use `--force-with-lease` para uma opção mais segura, que evita sobrescrever trabalho de outras pessoas se o remoto tiver sido atualizado.

```bash
git push origin motoshima --force-with-lease
```

**Explicação:**
- `git push origin motoshima`: Faz push para a branch `motoshima` no remoto `origin`.
- `--force-with-lease`: Força o push, mas verifica se o histórico remoto não foi alterado por outra pessoa desde o seu último fetch.

---

### Passo 5: Adicionar o arquivo ao `.gitignore` (para evitar problemas futuros)

Para garantir que esse arquivo (ou outros arquivos grandes similares) não sejam commitados novamente, adicione-o ao seu arquivo `.gitignore`.

Abra ou crie o arquivo `.gitignore` na raiz do seu repositório e adicione as seguintes linhas:

```gitignore
# Arquivos grandes ou de dados brutos
data/dbqueimadas_CSV.zip
# Você pode adicionar padrões para outros tipos de arquivos grandes também:
*.zip
*.csv
*.parquet
*.pkl
```

Em seguida, commite e faça push das alterações no `.gitignore`:

```bash
git add .gitignore
git commit -m "Adiciona arquivos grandes ao .gitignore"
git push origin motoshima
```

---

### Opcional: Usar Git LFS para versionar arquivos grandes

Se você **precisa** versionar arquivos grandes (acima de 100 MB), a solução correta é usar o [Git Large File Storage (LFS)](https://git-lfs.github.com/).

1.  **Instale o Git LFS.**
2.  **No seu repositório, configure o LFS para rastrear o tipo de arquivo:**
    ```bash
    git lfs install
    git lfs track "*.zip" # ou o padrão do seu arquivo
    ```
3.  **Adicione o arquivo e o `.gitattributes` (criado pelo LFS) e commite:**
    ```bash
    git add .gitattributes
    git add data/dbqueimadas_CSV.zip
    git commit -m "Adiciona arquivo grande com Git LFS"
    git push origin motoshima
    ```

Lembre-se que, mesmo usando LFS, você ainda precisaria remover o arquivo do histórico "normal" (Passos 1-4) se ele já foi commitado sem o LFS.
```