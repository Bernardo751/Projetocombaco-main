-- Banco base do sistema. Use apenas dados fictícios durante os testes.
CREATE DATABASE IF NOT EXISTS estudio_tatuagem
  CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE estudio_tatuagem;

CREATE TABLE IF NOT EXISTS senioridade (
  idsenioridade INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS estilo (
  idestilo INT AUTO_INCREMENT PRIMARY KEY,
  descricao VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS cliente (
  idcliente INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  cpf CHAR(11) NOT NULL UNIQUE,
  telefone VARCHAR(20),
  datacadastro DATE,
  cidade VARCHAR(100),
  uf CHAR(2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS tatuador (
  idtatuador INT AUTO_INCREMENT PRIMARY KEY,
  nometatuador VARCHAR(100) NOT NULL,
  cpf CHAR(11) NOT NULL UNIQUE,
  email VARCHAR(100),
  telefone VARCHAR(20),
  datacontratacao DATE,
  idsenioridade INT NOT NULL,
  CONSTRAINT fk_tatuador_senioridade FOREIGN KEY (idsenioridade) REFERENCES senioridade(idsenioridade)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS tatuador_estilo (
  idtatuador INT NOT NULL,
  idestilo INT NOT NULL,
  dataestilo DATE,
  PRIMARY KEY (idtatuador, idestilo),
  CONSTRAINT fk_te_tatuador FOREIGN KEY (idtatuador) REFERENCES tatuador(idtatuador),
  CONSTRAINT fk_te_estilo FOREIGN KEY (idestilo) REFERENCES estilo(idestilo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS agendamento (
  idagendamento INT AUTO_INCREMENT PRIMARY KEY,
  idcliente INT NOT NULL,
  idtatuador INT NOT NULL,
  dataagendamento DATE NOT NULL,
  horaagendamento TIME NOT NULL,
  descricaotatuagem TEXT,
  desenhoaprovado VARCHAR(255),
  valortatuagem DECIMAL(10,2),
  status ENUM('pendente','confirmado','concluido','cancelado') NOT NULL DEFAULT 'pendente',
  CONSTRAINT fk_ag_cliente FOREIGN KEY (idcliente) REFERENCES cliente(idcliente),
  CONSTRAINT fk_ag_tatuador FOREIGN KEY (idtatuador) REFERENCES tatuador(idtatuador)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS usuario (
  idusuario INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  senha VARCHAR(255) NOT NULL,
  tipo ENUM('admin','funcionario','cliente') NOT NULL DEFAULT 'funcionario',
  idcliente INT NULL,
  CONSTRAINT fk_usuario_cliente FOREIGN KEY (idcliente) REFERENCES cliente(idcliente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT IGNORE INTO senioridade (nome) VALUES ('Júnior'), ('Pleno'), ('Sênior');
INSERT IGNORE INTO estilo (descricao) VALUES ('Blackwork'), ('Aquarela'), ('Realismo'), ('Old School');

