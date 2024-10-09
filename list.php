<?php

// Create (or open) a SQLite database
$pdo = new PDO('sqlite:./data.sqlite3');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Query data
$stmt = $pdo->query('SELECT * FROM events');
$events = $stmt->fetchAll(PDO::FETCH_ASSOC);

?>
<table>
    <tr>
        <th>ID</th>
        <th>name</th>
        <th>Image</th>
    </tr>
<?php
foreach ($events as $row) {
    ?>
        <tr>
            <td><?= $row['id'] ?></td>
            <td><?= $row['name'] ?></td>
            <?php
            $ext = match (true) {
                file_exists('./images/marian-miracles/'.$row['id'].'.jpg') => 'jpg',
                file_exists('./images/marian-miracles/'.$row['id'].'.JPG') => 'JPG',
                file_exists('./images/marian-miracles/'.$row['id'].'.png') => 'png',
                file_exists('./images/marian-miracles/'.$row['id'].'.webm') => 'webm',
                default => 'none',
            };
            ?>
            <td><img src="images/marian-miracles/<?= $row['id'] ?>.<?= $ext ?>" height=100></td>
        </tr>
    <?php
}
?>
</table>
