<script>
	import Data from "./Data.svelte";
	import Validate from "./Validate.svelte";
  import Search  from "./Search.svelte";
	export let menu = 0;
</script>

<div class="text-center">
  <button type="button" class="btn btn-outline-primary"><a class="text-decoration-none fs-4" href="/" on:click|preventDefault={() => (menu = 1)}>Get Data</a></button>
  <button type="button" class="btn btn-outline-primary"><a class="text-decoration-none fs-4" href="/" on:click|preventDefault={() => (menu = 2)}>Validate</a></button>
  <button type="button" class="btn btn-outline-primary"><a class="text-decoration-none fs-4" href="/" on:click|preventDefault={() => (menu = 3)}>Query</a></button>
</div>

{#if menu === 1}
<Data />
{:else if menu === 2}
<Validate />
{:else if menu === 3}
<Search />
{/if}