<!DOCTYPE html>
<html>
<head>
    <title>ERC20 Contract</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container"><?php 
//load eth_erc20.json 
/*
 {
        "contract_address": "0xdc0327d50e6c73db2f8117760592c8bbf1cdcf38",
        "sourceScanned": "processed",
        "holders": {
            "ETH": 31084
        },
        "p8skip": true
    },
    {
        "contract_address": "0x251f48fdf1a4736de096d2e77e724b34c8dc8773",
        "sourceScanned": "processed",
        "web_domains": [
            "www.dex-ai.ai",
            "dex-ai.app",
            "dex-ai.gitbook.io"
        ],
        "telegram_groups": [
            "dexaierc"
        ],
        "holders": {
            "ETH": 696
        },
        "p6": true,
        "myuser": 6761555344,
        "tgGroupJoined": "error: Can't send messages",
        "p8": true,
        "p8skip": true
    },
*/

//sync eth_erc20.json with https://github.com/noxonsu/smartTokenlist/blob/main/eth_erc20.json once a hour
if(filectime('eth_erc20.json') < time() - 3600){
    echo    'sync eth_erc20.json with ';
    $url = 'https://raw.githubusercontent.com/noxonsu/smartTokenlist/main/eth_erc20.json';
    $json = file_get_contents($url);
    file_put_contents('eth_erc20.json', $json);
}

//find only contract with p6 = true 
$json = file_get_contents('eth_erc20.json');
$data = json_decode($json, true);
//reverse array
$data = array_reverse($data);
$contract = array();
foreach ($data as $key => $value) {
    if($value['p6'] == true){
        $contract[] = $value;
    }
}

//bootstrap html init
$filectime = filectime('eth_erc20.json');


if ($_GET['a'] == 'details') {
    $contract_address = $_GET['contract'];

    //xss prevent . allow only ethereum address
    if(!preg_match('/^0x[a-fA-F0-9]{40}$/', $contract_address)){
        die('Invalid contract address');
    }

    $contract = array();
    foreach ($data as $key => $value) {
        if($value['contract_address'] == $contract_address){
            $contract = $value;
        }
    }
    ?><h1>Contract: <?php echo $contract_address; ?></h1><?

    ?><h2>WebSite</h2><?
    if(isset($contract['web_domains'])){
        foreach ($contract['web_domains'] as $key => $web) {
            echo '<a href="http://'.$web.'" rel="nofollow" target="_blank">'.$web.'</a><br>';
        }
    }
    ?><h2>Summary</h2><?
    //load https://github.com/noxonsu/smartTokenlist/blob/main/summaries/contract.json to summary/{contract}.json if not exist
    $summary = array();
    $summary_file = 'summaries/'.$contract_address.'.json';
    if(!file_exists($summary_file)){
        $url = 'https://raw.githubusercontent.com/noxonsu/smartTokenlist/main/summaries/'.$contract_address.'.json';
        $json = file_get_contents($url);
        file_put_contents($summary_file, $json);
    }
    $summary = json_decode(file_get_contents($summary_file), true);
    echo $summary['summary'];

    
    ?><h2>Telegram groups:</h2><?
    if(isset($contract['telegram_groups'])){
        foreach ($contract['telegram_groups'] as $key => $tg) {
            echo $tg.'<br>';
        }
    }
    
    ?><h3>Similar projects</h3><?
    //find previous 3 contracts in eth_erc20.json after this contract only if p6 = true
    $similar = array();
    $found = false;
    foreach ($data as $key => $value) {
        if($found == true && $value['p6'] == true){
            $similar[] = $value;
        }
        if($value['contract_address'] == $contract_address){
            $found = true;
        }
        if(count($similar) == 3){
            break;
        }
    }
    foreach ($similar as $key => $value) {
        echo '<a href="?a=details&contract='.$value['contract_address'].'" rel="nofollow" target="_blank">'.$value['contract_address'].'</a><br>';
    }
    
} else {
?>

        <h2>ERC20 Contracts (latest on top). Latest update: <?php echo date('Y-m-d H:i:s',$filectime); ?></h2>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Contract Address</th>
                    <th>Web Domain</th>
                    <th>Telegram Groups</th>
                    <th>ETH Holders</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($contract as $key => $value) { ?>
                    <tr>
                        <td><a href="?a=details&contract=<?php echo $value['contract_address']; ?>"><?php echo $value['contract_address']; ?></a></td>
                        <td>
                            <?php 
                            if(isset($value['web_domains'])){
                                foreach ($value['web_domains'] as $key => $web) {
                                    echo $web.'<br>';
                                }
                            }
                            ?>
                        </td>
                        <td>
                            <?php 
                            if(isset($value['telegram_groups'])){
                                foreach ($value['telegram_groups'] as $key => $tg) {
                                    echo $tg.'<br>';
                                }
                            }
                            ?>
                        </td>
                        <td><?php echo $value['holders']['ETH']; ?></td>
                    </tr>
                <?php } ?>
            </tbody>
        </table>
<?php } ?>
</div>
</body>
</html>