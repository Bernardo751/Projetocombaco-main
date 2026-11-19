-- Dados fictícios da aula 2. Use em um banco de estudo novo, após importar a estrutura.
-- Este arquivo não é um backup do banco que você já preencheu no seu computador.
USE estudio_tatuagem;

INSERT INTO tatuador (nometatuador, cpf, email, telefone, datacontratacao, idsenioridade)
SELECT 'Lucas Mendes', '11111111111', 'lucas@estudio.com', '11999990001', '2020-03-01', idsenioridade
FROM senioridade WHERE nome='Sênior' AND NOT EXISTS (SELECT 1 FROM tatuador WHERE cpf='11111111111');
INSERT INTO tatuador (nometatuador, cpf, email, telefone, datacontratacao, idsenioridade)
SELECT 'Carla Souza', '22222222222', 'carla@estudio.com', '11999990002', '2022-06-15', idsenioridade
FROM senioridade WHERE nome='Pleno' AND NOT EXISTS (SELECT 1 FROM tatuador WHERE cpf='22222222222');
INSERT INTO tatuador (nometatuador, cpf, email, telefone, datacontratacao, idsenioridade)
SELECT 'Pedro Lima', '33333333333', 'pedro@estudio.com', '11999990003', '2024-01-10', idsenioridade
FROM senioridade WHERE nome='Júnior' AND NOT EXISTS (SELECT 1 FROM tatuador WHERE cpf='33333333333');

INSERT INTO cliente (nome, cpf, telefone, datacadastro, cidade, uf)
SELECT 'Ana Silva', '44444444444', '11988880001', '2024-01-15', 'São Paulo', 'SP'
WHERE NOT EXISTS (SELECT 1 FROM cliente WHERE cpf='44444444444');
INSERT INTO cliente (nome, cpf, telefone, datacadastro, cidade, uf)
SELECT 'Bruno Costa', '55555555555', '31988880002', '2024-03-22', 'Belo Horizonte', 'MG'
WHERE NOT EXISTS (SELECT 1 FROM cliente WHERE cpf='55555555555');

INSERT IGNORE INTO tatuador_estilo (idtatuador, idestilo, dataestilo)
SELECT t.idtatuador, e.idestilo, dados.dataestilo
FROM (
    SELECT '11111111111' AS cpf, 'Blackwork' AS estilo, '2020-03-01' AS dataestilo
    UNION ALL SELECT '11111111111', 'Realismo', '2021-05-10'
    UNION ALL SELECT '22222222222', 'Aquarela', '2022-06-15'
    UNION ALL SELECT '33333333333', 'Old School', '2024-01-10'
) dados
JOIN tatuador t ON t.cpf=dados.cpf JOIN estilo e ON e.descricao=dados.estilo;

INSERT INTO agendamento (idcliente, idtatuador, dataagendamento, horaagendamento, descricaotatuagem, valortatuagem)
SELECT c.idcliente, t.idtatuador, '2025-05-10', '14:00:00', 'Mandala no braço', 350.00
FROM cliente c JOIN tatuador t ON t.cpf='11111111111'
WHERE c.cpf='44444444444' AND NOT EXISTS (
  SELECT 1 FROM agendamento a WHERE a.idcliente=c.idcliente AND a.descricaotatuagem='Mandala no braço'
);
INSERT INTO agendamento (idcliente, idtatuador, dataagendamento, horaagendamento, descricaotatuagem, valortatuagem)
SELECT c.idcliente, t.idtatuador, '2025-05-11', '10:00:00', 'Rosa aquarela no ombro', 200.00
FROM cliente c JOIN tatuador t ON t.cpf='22222222222'
WHERE c.cpf='55555555555' AND NOT EXISTS (
  SELECT 1 FROM agendamento a WHERE a.idcliente=c.idcliente AND a.descricaotatuagem='Rosa aquarela no ombro'
);
