-- Agendamentos de chegada para DEMO (proximos dias) - rode no kingstar_wms.
-- Alimenta a ferramenta agenda_de_chegada da AYDA.
USE kingstar_wms;

INSERT IGNORE INTO agendamentos (id, fornecedor_nome, numero_nf, data_agendada, doca, status) VALUES
  (UUID(), 'Espumas Flex Brasil',   'NF-10001', NOW() + INTERVAL 1 DAY,  'DOCA-01', 'AGENDADO'),
  (UUID(), 'Molas Pocket Premium',  'NF-10003', NOW() + INTERVAL 1 DAY,  'DOCA-02', 'AGENDADO'),
  (UUID(), 'Madeiras Box Forte',    'NF-10008', NOW() + INTERVAL 2 DAY,  'DOCA-01', 'AGENDADO'),
  (UUID(), 'Estofa Tecidos Norte',  'NF-10010', NOW() + INTERVAL 3 DAY,  'DOCA-03', 'AGENDADO'),
  (UUID(), 'Ferragens & Pes Uniao', 'NF-10011', NOW() + INTERVAL 5 DAY,  'DOCA-02', 'AGENDADO'),
  (UUID(), 'Tecidos & Malhas Sul',  'NF-10018', NOW() + INTERVAL 6 DAY,  'DOCA-01', 'AGENDADO');
