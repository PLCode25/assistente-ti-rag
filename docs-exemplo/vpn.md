# Acesso remoto via VPN

Este guia explica como se conectar à rede da empresa fora do escritório usando a VPN corporativa.

## Instalação do cliente

1. Abra o Portal de Software da empresa.
2. Procure por "Cliente VPN Corporativo" e clique em Instalar.
3. Reinicie o computador ao final da instalação.

Usuários de Linux devem baixar o pacote .deb ou .rpm na página de downloads da intranet.

## Primeira conexão

Abra o cliente VPN e informe o endereço do servidor: vpn.empresa.exemplo. Use seu usuário de rede (o mesmo do e-mail, sem o domínio) e a sua senha. Na primeira conexão será solicitado o código do autenticador (MFA) cadastrado no celular.

## Problemas comuns

### Erro "Falha de autenticação"

Verifique se a senha não expirou. Senhas de rede expiram a cada 90 dias. Se a senha estiver correta, confira se o horário do celular está sincronizado automaticamente, pois códigos MFA dependem do horário.

### Conecta, mas sistemas internos não abrem

Desconecte e conecte novamente. Se persistir, limpe o cache de DNS: no Windows, execute `ipconfig /flushdns` no Prompt de Comando. Em redes de hotéis ou aeroportos, conclua o login no portal da rede Wi-Fi antes de iniciar a VPN.

### Conexão cai com frequência

Prefira redes cabeadas ou Wi-Fi de 5 GHz. Desative outras VPNs ou proxies pessoais. Se as quedas continuarem, abra um chamado informando o horário das quedas.
