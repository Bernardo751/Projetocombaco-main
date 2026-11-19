-- Atualização opcional da estrutura da versão anterior; exporte seu banco antes.
-- Não apaga registros e não cria outra conta de administrador.
USE estudio_tatuagem;
ALTER TABLE usuario MODIFY email VARCHAR(150) NOT NULL;
ALTER TABLE agendamento MODIFY desenhoaprovado VARCHAR(255);
