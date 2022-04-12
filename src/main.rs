extern crate reqwest;
use scraper::{Html, Selector};
use serde_json::json;
use serenity::{
    async_trait,
    client::Context,
    model::{channel::Message},
    prelude::*,
    framework::standard::StandardFramework,
};

static FAC_URL: &str = "https://macreconline.ca/FacilityOccupancy/GetFacilityData";
#[allow(dead_code)]
static DISCORD_TOKEN: &str = "";

async fn get_faculty_data() -> Vec<std::string::String> {
    let sports_hall: serde_json::Value = json!({
        "facilityId": "0986c0ef-0cc6-4659-9f7c-925af22a98c6",
        "occupancyDisplayType": "00000000-0000-0000-0000-000000004488" }
    );

    let popup: serde_json::Value = json!({
        "facilityId": "7a0d7831-5fa8-4bfb-804b-0128d1dd6a18",
        "occupancyDisplayType": "00000000-0000-0000-0000000000004488"}
    );

    let track: serde_json::Value = json!({
         "facilityId": "da4739b0-2ecb-4a55-9247-b411669f4ad8",
         "occupancyDisplayType": "00000000-0000-0000-0000000000004488"}
    );
    let client = reqwest::Client::new();
    let mut response = vec![];
    for facility in [sports_hall, popup, track].iter() {
        let res = client.post(FAC_URL).json(facility).send().await.unwrap();
        response.push(res.text().await.unwrap());
    }
    response
}

async fn parse_html(html: &String) -> Vec<String> {
    let document = Html::parse_document(&html);
    let selector = Selector::parse("p").unwrap();

    let mut response = vec![];
    for elem in document.select(&selector) {
        let text = elem.text().collect();
        response.push(text);
    }
    response
}

struct Handler;

#[async_trait]
impl EventHandler for Handler {
    async fn message(&self, context: Context, msg: Message) {
        if msg.content == "!pulse" {
            let data = get_faculty_data().await;
            let result = parse_html(&data[0]).await;
            let _ = msg.channel_id.say(&context.http, result.join("\n")).await;
        }
    }
}

#[tokio::main]
async fn main() {
    let mut client = Client::builder(&DISCORD_TOKEN)
        .event_handler(Handler)
        .framework(
            StandardFramework::new()
        )
        .await
        .expect("Error creating client");
    if let Err(err) = client.start().await {
        println!("Error: {:?}", err);
    }
}
