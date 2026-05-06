# Logos dos clubes

Coloque aqui os arquivos de logo dos clubes do Brasileirão 2017.

## Formato e nomenclatura

- Formatos aceitos: `.png`, `.svg`, `.jpg`, `.webp` (PNG transparente é o ideal).
- Tamanho recomendado: 200×200 px ou maior, com fundo transparente.
- O nome do arquivo deve ser exatamente o **slug** definido em `src/teams.py`.

## Mapeamento clube → arquivo

| Clube                | Arquivo                       |
|----------------------|-------------------------------|
| Corinthians          | `corinthians.png`             |
| Palmeiras            | `palmeiras.png`               |
| Santos               | `santos.png`                  |
| Gremio               | `gremio.png`                  |
| Cruzeiro             | `cruzeiro.png`                |
| Flamengo             | `flamengo.png`                |
| Vasco Da Gama RJ     | `vasco.png`                   |
| Chapecoense          | `chapecoense.png`             |
| Atletico Mineiro     | `anetletico-miiro.png`        |
| Botafogo RJ          | `botafogo.png`                |
| Atletico Paranaense  | `atletico-paranaense.png`     |
| EC Bahia             | `bahia.png`                   |
| Sao Paulo            | `sao-paulo.png`               |
| Fluminense           | `fluminense.png`              |
| Sport Recife         | `sport.png`                   |
| Vitoria              | `vitoria.png`                 |
| Coritiba             | `coritiba.png`                |
| Avai                 | `avai.png`                    |
| Ponte Preta          | `ponte-preta.png`             |
| Atletico Goianiense  | `atletico-goianiense.png`     |

## Comportamento sem os logos

Se um arquivo de logo não existir, o dashboard exibe automaticamente um **badge circular com a abreviação** do clube (ex.: "FLA", "COR") usando a cor oficial. Você pode usar o dashboard normalmente sem nenhum logo, ou ir adicionando aos poucos — o app detecta a presença dos arquivos a cada reload.
